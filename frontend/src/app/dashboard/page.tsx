"use client";

import { useEffect, useState } from "react";
import {
    AlertTriangle,
    CheckCircle,
    Clock,
    Camera,
} from "lucide-react";
import api from "@/lib/api";

interface StatsData {
    total: number;
    critical: number;
    resolved: number;
    pending: number;
}

interface Detection {
    id: string;
    severity: string;
    confidence_score: number;
    status: string;
    created_at: string;
    description: string | null;
}

export default function DashboardPage() {
    const [stats, setStats] = useState<StatsData>({
        total: 0,
        critical: 0,
        resolved: 0,
        pending: 0,
    });
    const [recentDetections, setRecentDetections] = useState<Detection[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const res = await api.get("/api/v1/detections/?page=1&page_size=5");
            const items: Detection[] = res.data.items || [];
            const total = res.data.total || 0;

            setRecentDetections(items);
            setStats({
                total,
                critical: items.filter((d) => d.severity === "critical").length,
                resolved: items.filter((d) => d.status === "resolved").length,
                pending: items.filter((d) => d.status === "detected").length,
            });
        } catch {
            // Backend not connected yet -- show empty state
        } finally {
            setLoading(false);
        }
    };

    const statCards = [
        {
            label: "Total Detections",
            value: stats.total,
            icon: Camera,
            color: "text-indigo-400",
            bg: "bg-indigo-500/10",
            border: "border-indigo-500/20",
        },
        {
            label: "Critical",
            value: stats.critical,
            icon: AlertTriangle,
            color: "text-red-400",
            bg: "bg-red-500/10",
            border: "border-red-500/20",
        },
        {
            label: "Resolved",
            value: stats.resolved,
            icon: CheckCircle,
            color: "text-green-400",
            bg: "bg-green-500/10",
            border: "border-green-500/20",
        },
        {
            label: "Pending Review",
            value: stats.pending,
            icon: Clock,
            color: "text-amber-400",
            bg: "bg-amber-500/10",
            border: "border-amber-500/20",
        },
    ];

    const severityBadge = (severity: string) => {
        const styles: Record<string, string> = {
            critical: "bg-red-500/10 text-red-400 border-red-500/20",
            high: "bg-orange-500/10 text-orange-400 border-orange-500/20",
            medium: "bg-amber-500/10 text-amber-400 border-amber-500/20",
            low: "bg-green-500/10 text-green-400 border-green-500/20",
        };
        return (
            <span
                className={`px-2 py-1 text-xs font-medium rounded-md border ${styles[severity] || styles.low
                    }`}
            >
                {severity}
            </span>
        );
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-96">
                <div className="animate-pulse text-gray-400">Loading dashboard...</div>
            </div>
        );
    }

    return (
        <div>
            <div className="mb-8">
                <h1 className="text-2xl font-bold text-white">Dashboard</h1>
                <p className="text-gray-400 mt-1">
                    Overview of pothole detections and repair status
                </p>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                {statCards.map((card) => (
                    <div
                        key={card.label}
                        className={`${card.bg} border ${card.border} rounded-xl p-6`}
                    >
                        <div className="flex items-center justify-between mb-4">
                            <card.icon className={`w-6 h-6 ${card.color}`} />
                        </div>
                        <p className="text-3xl font-bold text-white">{card.value}</p>
                        <p className="text-sm text-gray-400 mt-1">{card.label}</p>
                    </div>
                ))}
            </div>

            {/* Recent Detections Table */}
            <div className="bg-gray-900 border border-gray-800 rounded-xl">
                <div className="p-6 border-b border-gray-800">
                    <h2 className="text-lg font-semibold text-white">
                        Recent Detections
                    </h2>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead>
                            <tr className="text-left text-sm text-gray-400 border-b border-gray-800">
                                <th className="px-6 py-3 font-medium">ID</th>
                                <th className="px-6 py-3 font-medium">Severity</th>
                                <th className="px-6 py-3 font-medium">Confidence</th>
                                <th className="px-6 py-3 font-medium">Status</th>
                                <th className="px-6 py-3 font-medium">Date</th>
                            </tr>
                        </thead>
                        <tbody>
                            {recentDetections.length === 0 ? (
                                <tr>
                                    <td
                                        colSpan={5}
                                        className="px-6 py-12 text-center text-gray-500"
                                    >
                                        No detections yet. Upload an image to get started.
                                    </td>
                                </tr>
                            ) : (
                                recentDetections.map((det) => (
                                    <tr
                                        key={det.id}
                                        className="border-b border-gray-800/50 hover:bg-gray-800/30 transition-colors"
                                    >
                                        <td className="px-6 py-4 text-sm text-gray-300 font-mono">
                                            {det.id.slice(0, 8)}...
                                        </td>
                                        <td className="px-6 py-4">{severityBadge(det.severity)}</td>
                                        <td className="px-6 py-4 text-sm text-gray-300">
                                            {(det.confidence_score * 100).toFixed(1)}%
                                        </td>
                                        <td className="px-6 py-4 text-sm text-gray-300 capitalize">
                                            {det.status}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-gray-400">
                                            {new Date(det.created_at).toLocaleDateString()}
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}

"use client";

import { useEffect, useState } from "react";
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    PieChart,
    Pie,
    Cell,
} from "recharts";
import Sidebar from "@/app/components/Sidebar";
import api from "@/lib/api";

interface Detection {
    severity: string;
    status: string;
    confidence_score: number;
    created_at: string;
}

const COLORS = {
    critical: "#ef4444",
    high: "#f97316",
    medium: "#f59e0b",
    low: "#22c55e",
};

const STATUS_COLORS = ["#6366f1", "#22c55e", "#f59e0b", "#ef4444"];

export default function AnalyticsPage() {
    const [severityData, setSeverityData] = useState<
        Array<{ name: string; count: number; fill: string }>
    >([]);
    const [statusData, setStatusData] = useState<
        Array<{ name: string; value: number }>
    >([]);
    const [totalDetections, setTotalDetections] = useState(0);
    const [avgConfidence, setAvgConfidence] = useState(0);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const res = await api.get("/api/v1/detections/?page=1&page_size=100");
            const items: Detection[] = res.data.items || [];
            const total = res.data.total || 0;

            setTotalDetections(total);

            // Severity distribution
            const sevCounts: Record<string, number> = {
                critical: 0,
                high: 0,
                medium: 0,
                low: 0,
            };
            items.forEach((d) => {
                if (sevCounts[d.severity] !== undefined) sevCounts[d.severity]++;
            });
            setSeverityData(
                Object.entries(sevCounts).map(([name, count]) => ({
                    name: name.charAt(0).toUpperCase() + name.slice(1),
                    count,
                    fill: COLORS[name as keyof typeof COLORS],
                }))
            );

            // Status distribution
            const statusCounts: Record<string, number> = {};
            items.forEach((d) => {
                statusCounts[d.status] = (statusCounts[d.status] || 0) + 1;
            });
            setStatusData(
                Object.entries(statusCounts).map(([name, value]) => ({
                    name: name.charAt(0).toUpperCase() + name.slice(1).replace(/_/g, " "),
                    value,
                }))
            );

            // Average confidence
            if (items.length > 0) {
                const avg =
                    items.reduce((sum, d) => sum + d.confidence_score, 0) / items.length;
                setAvgConfidence(avg);
            }
        } catch {
            // Backend offline
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex min-h-screen bg-gray-950">
                <Sidebar />
                <main className="ml-64 flex-1 p-8 flex items-center justify-center">
                    <div className="animate-pulse text-gray-400">Loading analytics...</div>
                </main>
            </div>
        );
    }

    return (
        <div className="flex min-h-screen bg-gray-950">
            <Sidebar />
            <main className="ml-64 flex-1 p-8">
                <div className="mb-8">
                    <h1 className="text-2xl font-bold text-white">Analytics</h1>
                    <p className="text-gray-400 mt-1">
                        Detection trends and severity breakdown
                    </p>
                </div>

                {/* Summary Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                        <p className="text-sm text-gray-400">Total Detections</p>
                        <p className="text-3xl font-bold text-white mt-2">
                            {totalDetections}
                        </p>
                    </div>
                    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                        <p className="text-sm text-gray-400">Avg Confidence</p>
                        <p className="text-3xl font-bold text-white mt-2">
                            {(avgConfidence * 100).toFixed(1)}%
                        </p>
                    </div>
                    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                        <p className="text-sm text-gray-400">Critical Rate</p>
                        <p className="text-3xl font-bold text-red-400 mt-2">
                            {totalDetections > 0
                                ? (
                                    ((severityData.find((s) => s.name === "Critical")?.count ||
                                        0) /
                                        totalDetections) *
                                    100
                                ).toFixed(1)
                                : 0}
                            %
                        </p>
                    </div>
                </div>

                {/* Charts */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Severity Bar Chart */}
                    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                        <h3 className="text-lg font-semibold text-white mb-6">
                            Severity Distribution
                        </h3>
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={severityData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                                <XAxis dataKey="name" stroke="#9ca3af" fontSize={12} />
                                <YAxis stroke="#9ca3af" fontSize={12} />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: "#1f2937",
                                        border: "1px solid #374151",
                                        borderRadius: "8px",
                                        color: "#fff",
                                    }}
                                />
                                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                                    {severityData.map((entry, index) => (
                                        <Cell key={index} fill={entry.fill} />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>

                    {/* Status Pie Chart */}
                    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                        <h3 className="text-lg font-semibold text-white mb-6">
                            Status Breakdown
                        </h3>
                        <ResponsiveContainer width="100%" height={300}>
                            <PieChart>
                                <Pie
                                    data={statusData}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={60}
                                    outerRadius={100}
                                    paddingAngle={4}
                                    dataKey="value"
                                    label={({ name, value }) => `${name}: ${value}`}
                                >
                                    {statusData.map((_, index) => (
                                        <Cell
                                            key={index}
                                            fill={STATUS_COLORS[index % STATUS_COLORS.length]}
                                        />
                                    ))}
                                </Pie>
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: "#1f2937",
                                        border: "1px solid #374151",
                                        borderRadius: "8px",
                                        color: "#fff",
                                    }}
                                />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </main>
        </div>
    );
}

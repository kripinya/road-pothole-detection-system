"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import Sidebar from "@/app/components/Sidebar";
import api from "@/lib/api";
import { MapPin } from "lucide-react";

// Dynamic import to avoid SSR issues with Leaflet
const MapView = dynamic(() => import("@/app/components/MapView"), {
    ssr: false,
    loading: () => (
        <div className="h-[600px] bg-gray-900 rounded-xl flex items-center justify-center">
            <div className="animate-pulse text-gray-400">Loading map...</div>
        </div>
    ),
});

interface Detection {
    id: string;
    latitude: number | null;
    longitude: number | null;
    severity: string;
    confidence_score: number;
    status: string;
}

export default function MapPage() {
    const [markers, setMarkers] = useState<
        Array<{
            id: string;
            lat: number;
            lng: number;
            severity: string;
            confidence: number;
            status: string;
        }>
    >([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchDetections();
    }, []);

    const fetchDetections = async () => {
        try {
            const res = await api.get("/api/v1/detections/?page=1&page_size=100");
            const items: Detection[] = res.data.items || [];

            const valid = items
                .filter((d) => d.latitude !== null && d.longitude !== null)
                .map((d) => ({
                    id: d.id,
                    lat: d.latitude!,
                    lng: d.longitude!,
                    severity: d.severity,
                    confidence: d.confidence_score,
                    status: d.status,
                }));

            setMarkers(valid);
        } catch {
            // Backend offline
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex min-h-screen bg-gray-950">
            <Sidebar />
            <main className="ml-64 flex-1 p-8">
                <div className="mb-8">
                    <h1 className="text-2xl font-bold text-white">Map View</h1>
                    <p className="text-gray-400 mt-1">
                        Geographic visualization of detected potholes
                    </p>
                </div>

                {/* Stats bar */}
                <div className="flex items-center gap-6 mb-4">
                    <div className="flex items-center gap-2">
                        <MapPin className="w-4 h-4 text-indigo-400" />
                        <span className="text-sm text-gray-400">
                            {markers.length} locations mapped
                        </span>
                    </div>
                    <div className="flex items-center gap-4 text-xs">
                        <span className="flex items-center gap-1">
                            <span className="w-3 h-3 rounded-full bg-red-500" /> Critical
                        </span>
                        <span className="flex items-center gap-1">
                            <span className="w-3 h-3 rounded-full bg-orange-500" /> High
                        </span>
                        <span className="flex items-center gap-1">
                            <span className="w-3 h-3 rounded-full bg-amber-500" /> Medium
                        </span>
                        <span className="flex items-center gap-1">
                            <span className="w-3 h-3 rounded-full bg-green-500" /> Low
                        </span>
                    </div>
                </div>

                {loading ? (
                    <div className="h-[600px] bg-gray-900 rounded-xl flex items-center justify-center">
                        <div className="animate-pulse text-gray-400">Loading map...</div>
                    </div>
                ) : (
                    <MapView markers={markers} />
                )}
            </main>
        </div>
    );
}

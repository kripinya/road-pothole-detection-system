"use client";

import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";

interface PotholeMarker {
    id: string;
    lat: number;
    lng: number;
    severity: string;
    confidence: number;
    status: string;
}

const severityColors: Record<string, string> = {
    critical: "#ef4444",
    high: "#f97316",
    medium: "#f59e0b",
    low: "#22c55e",
};

export default function MapView({ markers }: { markers: PotholeMarker[] }) {
    return (
        <MapContainer
            center={[28.6139, 77.209]}
            zoom={12}
            className="h-full w-full rounded-xl"
            style={{ minHeight: "600px" }}
        >
            <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>'
                url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            />
            {markers.map((m) => (
                <CircleMarker
                    key={m.id}
                    center={[m.lat, m.lng]}
                    radius={8}
                    pathOptions={{
                        color: severityColors[m.severity] || "#22c55e",
                        fillColor: severityColors[m.severity] || "#22c55e",
                        fillOpacity: 0.7,
                    }}
                >
                    <Popup>
                        <div className="text-sm">
                            <p className="font-bold capitalize">{m.severity} severity</p>
                            <p>Confidence: {(m.confidence * 100).toFixed(1)}%</p>
                            <p>Status: {m.status}</p>
                        </div>
                    </Popup>
                </CircleMarker>
            ))}
        </MapContainer>
    );
}

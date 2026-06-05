"use client";

import { useState, useCallback } from "react";
import { Upload, FileImage, Loader2, AlertTriangle, CheckCircle } from "lucide-react";
import Sidebar from "@/app/components/Sidebar";
import api from "@/lib/api";

interface AnalysisResult {
    detection: {
        image_width: number;
        image_height: number;
        detections: Array<{
            class_name: string;
            confidence: number;
            bbox: { x_min: number; y_min: number; x_max: number; y_max: number };
        }>;
        inference_time_ms: number;
    };
    analysis: {
        perception: {
            pothole_count: number;
            overall_estimated_size: string;
            confidence_avg: number;
        };
        severity: {
            score: number;
            classification: string;
            reasoning: string;
        };
        priority: {
            priority_score: number;
            estimated_cost_inr: number;
            recommended_action: string;
            repair_timeline: string;
        };
        agent_logs: string[];
        pipeline_time_ms: number;
    };
}

export default function UploadPage() {
    const [file, setFile] = useState<File | null>(null);
    const [preview, setPreview] = useState<string | null>(null);
    const [uploading, setUploading] = useState(false);
    const [result, setResult] = useState<AnalysisResult | null>(null);
    const [error, setError] = useState("");

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        const dropped = e.dataTransfer.files[0];
        if (dropped && dropped.type.startsWith("image/")) {
            setFile(dropped);
            setPreview(URL.createObjectURL(dropped));
            setResult(null);
            setError("");
        }
    }, []);

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const selected = e.target.files?.[0];
        if (selected) {
            setFile(selected);
            setPreview(URL.createObjectURL(selected));
            setResult(null);
            setError("");
        }
    };

    const handleUpload = async () => {
        if (!file) return;
        setUploading(true);
        setError("");

        try {
            const formData = new FormData();
            formData.append("file", file);

            const res = await api.post("/api/v1/detections/", formData, {
                headers: { "Content-Type": "multipart/form-data" },
            });

            // The backend returns the detection record; fetch full analysis separately
            if (res.data.ai_analysis) {
                setResult({
                    detection: res.data.bbox_data,
                    analysis: res.data.ai_analysis,
                });
            } else {
                setResult(null);
                setError("Detection saved but ML analysis unavailable. Is the ML service running?");
            }
        } catch (err: unknown) {
            const axiosErr = err as { response?: { data?: { detail?: string } } };
            setError(axiosErr.response?.data?.detail || "Upload failed");
        } finally {
            setUploading(false);
        }
    };

    const severityColor: Record<string, string> = {
        critical: "text-red-400",
        high: "text-orange-400",
        medium: "text-amber-400",
        low: "text-green-400",
    };

    return (
        <div className="flex min-h-screen bg-gray-950">
            <Sidebar />
            <main className="ml-64 flex-1 p-8">
                <div className="mb-8">
                    <h1 className="text-2xl font-bold text-white">Upload Image</h1>
                    <p className="text-gray-400 mt-1">
                        Upload a road image for pothole detection and AI analysis
                    </p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Left: Upload Area */}
                    <div>
                        {/* Drop Zone */}
                        <div
                            onDragOver={(e) => e.preventDefault()}
                            onDrop={handleDrop}
                            className="border-2 border-dashed border-gray-700 rounded-xl p-12 text-center hover:border-indigo-500/50 transition-colors cursor-pointer"
                            onClick={() => document.getElementById("file-input")?.click()}
                        >
                            {preview ? (
                                <img
                                    src={preview}
                                    alt="Preview"
                                    className="max-h-64 mx-auto rounded-lg object-contain"
                                />
                            ) : (
                                <div>
                                    <Upload className="w-12 h-12 text-gray-500 mx-auto mb-4" />
                                    <p className="text-gray-400 mb-2">
                                        Drag and drop an image here, or click to browse
                                    </p>
                                    <p className="text-gray-600 text-sm">
                                        Supports JPG, PNG, WEBP (max 10MB)
                                    </p>
                                </div>
                            )}
                            <input
                                id="file-input"
                                type="file"
                                accept="image/*"
                                onChange={handleFileSelect}
                                className="hidden"
                            />
                        </div>

                        {file && (
                            <div className="mt-4 flex items-center justify-between bg-gray-900 border border-gray-800 rounded-lg p-4">
                                <div className="flex items-center gap-3">
                                    <FileImage className="w-5 h-5 text-indigo-400" />
                                    <div>
                                        <p className="text-sm text-white">{file.name}</p>
                                        <p className="text-xs text-gray-500">
                                            {(file.size / 1024 / 1024).toFixed(2)} MB
                                        </p>
                                    </div>
                                </div>
                                <button
                                    onClick={handleUpload}
                                    disabled={uploading}
                                    className="px-6 py-2 bg-indigo-500 hover:bg-indigo-600 text-white text-sm font-medium rounded-lg transition-colors disabled:opacity-50"
                                >
                                    {uploading ? (
                                        <Loader2 className="w-4 h-4 animate-spin" />
                                    ) : (
                                        "Analyze"
                                    )}
                                </button>
                            </div>
                        )}

                        {error && (
                            <div className="mt-4 p-4 bg-red-500/10 border border-red-500/20 rounded-lg flex items-center gap-3">
                                <AlertTriangle className="w-5 h-5 text-red-400 shrink-0" />
                                <p className="text-sm text-red-400">{error}</p>
                            </div>
                        )}
                    </div>

                    {/* Right: Analysis Results */}
                    <div>
                        {result ? (
                            <div className="space-y-4">
                                {/* Severity Card */}
                                <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                                    <h3 className="text-sm font-medium text-gray-400 mb-3">
                                        Severity Assessment
                                    </h3>
                                    <div className="flex items-center gap-4 mb-3">
                                        <span
                                            className={`text-4xl font-bold ${severityColor[result.analysis.severity.classification] ||
                                                "text-white"
                                                }`}
                                        >
                                            {result.analysis.severity.score.toFixed(0)}
                                        </span>
                                        <span
                                            className={`px-3 py-1 text-sm font-medium rounded-lg border ${result.analysis.severity.classification === "critical"
                                                    ? "bg-red-500/10 text-red-400 border-red-500/20"
                                                    : result.analysis.severity.classification === "high"
                                                        ? "bg-orange-500/10 text-orange-400 border-orange-500/20"
                                                        : result.analysis.severity.classification === "medium"
                                                            ? "bg-amber-500/10 text-amber-400 border-amber-500/20"
                                                            : "bg-green-500/10 text-green-400 border-green-500/20"
                                                }`}
                                        >
                                            {result.analysis.severity.classification.toUpperCase()}
                                        </span>
                                    </div>
                                    <p className="text-sm text-gray-400">
                                        {result.analysis.severity.reasoning}
                                    </p>
                                </div>

                                {/* Perception Card */}
                                <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                                    <h3 className="text-sm font-medium text-gray-400 mb-3">
                                        Detection Summary
                                    </h3>
                                    <div className="grid grid-cols-2 gap-4">
                                        <div>
                                            <p className="text-2xl font-bold text-white">
                                                {result.analysis.perception.pothole_count}
                                            </p>
                                            <p className="text-xs text-gray-500">Potholes Found</p>
                                        </div>
                                        <div>
                                            <p className="text-2xl font-bold text-white capitalize">
                                                {result.analysis.perception.overall_estimated_size}
                                            </p>
                                            <p className="text-xs text-gray-500">Largest Size</p>
                                        </div>
                                    </div>
                                </div>

                                {/* Priority Card */}
                                <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                                    <h3 className="text-sm font-medium text-gray-400 mb-3">
                                        Repair Recommendation
                                    </h3>
                                    <div className="space-y-3">
                                        <div className="flex justify-between">
                                            <span className="text-sm text-gray-500">Timeline</span>
                                            <span className="text-sm text-white">
                                                {result.analysis.priority.repair_timeline.replace(/_/g, " ")}
                                            </span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-sm text-gray-500">Est. Cost</span>
                                            <span className="text-sm text-white">
                                                INR {result.analysis.priority.estimated_cost_inr.toLocaleString()}
                                            </span>
                                        </div>
                                        <div className="pt-3 border-t border-gray-800">
                                            <p className="text-sm text-gray-300">
                                                {result.analysis.priority.recommended_action}
                                            </p>
                                        </div>
                                    </div>
                                </div>

                                {/* Agent Logs */}
                                <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                                    <h3 className="text-sm font-medium text-gray-400 mb-3">
                                        Agent Pipeline Log
                                    </h3>
                                    <div className="space-y-1">
                                        {result.analysis.agent_logs.map((log, i) => (
                                            <div key={i} className="flex items-center gap-2">
                                                <CheckCircle className="w-3 h-3 text-green-500 shrink-0" />
                                                <span className="text-xs text-gray-400 font-mono">
                                                    {log}
                                                </span>
                                            </div>
                                        ))}
                                    </div>
                                    <p className="text-xs text-gray-600 mt-3">
                                        Pipeline completed in{" "}
                                        {result.analysis.pipeline_time_ms.toFixed(0)}ms
                                    </p>
                                </div>
                            </div>
                        ) : (
                            <div className="flex flex-col items-center justify-center h-full text-gray-600">
                                <FileImage className="w-16 h-16 mb-4" />
                                <p className="text-sm">Upload an image to see analysis results</p>
                            </div>
                        )}
                    </div>
                </div>
            </main>
        </div>
    );
}

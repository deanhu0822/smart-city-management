'use client';

import { useState } from 'react';

type ViewMode = '2D' | '3D';

// Minimal inline SVG icons
function CheckCircleIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#374151" strokeWidth="1.8">
      <circle cx="12" cy="12" r="10" />
      <path d="M8 12l3 3 5-5" />
    </svg>
  );
}

function RefreshIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#9CA3AF" strokeWidth="1.8">
      <path d="M23 4v6h-6" />
      <path d="M1 20v-6h6" />
      <path d="M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15" />
    </svg>
  );
}

function DotsIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="#9CA3AF">
      <circle cx="5" cy="12" r="1.5" />
      <circle cx="12" cy="12" r="1.5" />
      <circle cx="19" cy="12" r="1.5" />
    </svg>
  );
}

function CommentIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#9CA3AF" strokeWidth="1.8">
      <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" />
    </svg>
  );
}

// Stylised building footprint matching design.png
function Building3D() {
  return (
    <svg width="120" height="150" viewBox="0 0 120 150" fill="none">
      {/* Main building body */}
      <polygon points="25,40 75,20 110,55 60,75" fill="#1E3A5F" />
      <polygon points="25,40 60,75 60,130 25,95" fill="#172D4D" />
      <polygon points="110,55 60,75 60,130 110,105" fill="#243F63" />
      {/* Roof cutout / courtyard */}
      <polygon points="45,52 72,42 90,60 63,70" fill="#F3F4F6" />
      {/* Road / path */}
      <polygon points="55,130 70,130 80,150 65,150" fill="#E5E7EB" />
      <polygon points="20,110 35,95 40,100 25,115" fill="#E5E7EB" />
      {/* Small accent windows */}
      <rect x="30" y="70" width="8" height="10" rx="1" fill="#2563EB" opacity="0.5" />
      <rect x="42" y="80" width="8" height="10" rx="1" fill="#2563EB" opacity="0.4" />
      <rect x="80" y="75" width="8" height="10" rx="1" fill="#2563EB" opacity="0.4" />
      <rect x="92" y="85" width="8" height="10" rx="1" fill="#2563EB" opacity="0.3" />
    </svg>
  );
}

export default function UploadPage() {
  const [viewMode, setViewMode] = useState<ViewMode>('3D');

  return (
    <div style={{
      minHeight: '100vh',
      background: '#F3F4F6',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: 24,
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    }}>
      <div style={{
        width: '100%',
        maxWidth: 680,
        background: '#FFFFFF',
        borderRadius: 14,
        border: '1px solid #E5E7EB',
        boxShadow: '0 1px 6px rgba(0,0,0,0.07)',
        overflow: 'hidden',
      }}>

        {/* ── HEADER ── */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '12px 16px',
          borderBottom: '1px solid #F3F4F6',
        }}>
          {/* Title */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <CheckCircleIcon />
            <span style={{ fontSize: 15, fontWeight: 600, color: '#111827' }}>Result</span>
          </div>

          {/* Controls */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            {/* 2D / 3D toggle */}
            <div style={{
              display: 'flex',
              background: '#F3F4F6',
              borderRadius: 8,
              padding: 3,
              gap: 2,
            }}>
              {(['2D', '3D'] as ViewMode[]).map(mode => (
                <button
                  key={mode}
                  onClick={() => setViewMode(mode)}
                  style={{
                    padding: '4px 12px',
                    borderRadius: 6,
                    border: 'none',
                    cursor: 'pointer',
                    fontSize: 13,
                    fontWeight: 500,
                    transition: 'all 0.15s',
                    background: viewMode === mode ? '#1E293B' : 'transparent',
                    color: viewMode === mode ? '#FFFFFF' : '#6B7280',
                  }}
                >
                  {mode}
                </button>
              ))}
            </div>

            {/* Dots menu */}
            <button style={{
              background: 'none', border: 'none', cursor: 'pointer',
              padding: '4px 6px', borderRadius: 6,
              display: 'flex', alignItems: 'center',
            }}>
              <DotsIcon />
            </button>

            {/* Refresh */}
            <button style={{
              background: 'none', border: 'none', cursor: 'pointer',
              padding: '4px 6px', borderRadius: 6,
              display: 'flex', alignItems: 'center',
            }}>
              <RefreshIcon />
            </button>
          </div>
        </div>

        {/* ── CANVAS AREA ── */}
        <div style={{
          position: 'relative',
          background: '#FAFAFA',
          height: 380,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}>
          {/* Status label */}
          <div style={{
            marginTop: 18,
            fontSize: 12,
            color: '#9CA3AF',
            letterSpacing: '0.02em',
          }}>
            Ready for review
          </div>

          {/* 3D Building model */}
          <div style={{
            flex: 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            opacity: viewMode === '3D' ? 1 : 0.35,
            transition: 'opacity 0.2s',
          }}>
            <Building3D />
          </div>

          {/* Comment icon — bottom right */}
          <button style={{
            position: 'absolute',
            bottom: 14,
            right: 14,
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            padding: 6,
            borderRadius: 8,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}>
            <CommentIcon />
          </button>
        </div>
      </div>
    </div>
  );
}

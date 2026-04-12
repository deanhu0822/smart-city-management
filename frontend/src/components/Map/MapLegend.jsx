'use client';

/** Permanent marker legend items shown in all modes */
const MARKER_LEGEND = [
  {
    icon: (
      <svg width="16" height="16" viewBox="0 0 16 16">
        <circle cx="8" cy="8" r="7" fill="rgba(234,179,8,0.22)" stroke="#D97706" strokeWidth="2" />
        <text x="8" y="12" textAnchor="middle" fontSize="8" fontWeight="bold" fill="#FDE047">1</text>
      </svg>
    ),
    label: 'District',
  },
  {
    icon: (
      <svg width="16" height="16" viewBox="0 0 16 16">
        <circle cx="8" cy="8" r="5.5" fill="#10B981" stroke="#fff" strokeWidth="1.5" />
      </svg>
    ),
    label: 'Building',
  },
  {
    icon: (
      <span style={{ fontSize: 10, lineHeight: 1, color: '#FBBF24', display: 'block', textAlign: 'center', width: 16 }}>★</span>
    ),
    label: 'Priority highlight',
  },
];

export default function MapLegend() {

  return (
    <div style={{
      position: 'absolute', bottom: 10, left: 10, zIndex: 10,
      background: 'rgba(255,255,255,0.94)', backdropFilter: 'blur(8px)',
      border: '1px solid #E2E8F0', borderRadius: 10,
      padding: '9px 11px', display: 'flex', flexDirection: 'column', gap: 4,
      boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
      pointerEvents: 'none',
    }}>
      {/* Permanent map markers */}
      <div style={{ fontSize: 9, fontWeight: 700, color: '#64748B', letterSpacing: '0.1em', marginBottom: 2 }}>
        MAP MARKERS
      </div>
      {MARKER_LEGEND.map((item, i) => (
        <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{ width: 16, height: 16, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
            {item.icon}
          </span>
          <span style={{ fontSize: 10, color: '#334155', whiteSpace: 'nowrap' }}>{item.label}</span>
        </div>
      ))}
    </div>
  );
}

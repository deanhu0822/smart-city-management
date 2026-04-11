import { useMemo } from 'react';
import { useDashboard } from '../context/DashboardContext';
import { ENERGY_SITES, scoreColor } from '../data/sites';

function KVItem({ label, value, valueStyle }) {
  return (
    <div style={{ background: '#0B1120', borderRadius: 6, padding: '8px 10px' }}>
      <div style={{ fontSize: 10, color: '#475569', marginBottom: 2 }}>{label}</div>
      <div style={{ fontSize: 13, fontWeight: 600, ...valueStyle }}>{value}</div>
    </div>
  );
}

function ScoreRing({ score }) {
  const r = 32;
  const circ = 2 * Math.PI * r;
  const offset = circ * (1 - score / 100);
  const color = scoreColor(score);

  return (
    <div style={{ textAlign: 'center', marginBottom: 12 }}>
      <svg viewBox="0 0 72 72" width={72} height={72} style={{ display: 'block', margin: '0 auto' }}>
        <circle cx="36" cy="36" r={r} fill="none" stroke="#1E293B" strokeWidth="7" />
        <circle
          cx="36" cy="36" r={r} fill="none"
          stroke={color} strokeWidth="7"
          strokeDasharray={circ.toFixed(1)}
          strokeDashoffset={offset.toFixed(1)}
          strokeLinecap="round"
          transform="rotate(-90 36 36)"
        />
        <text x="36" y="41" textAnchor="middle" fill="#F1F5F9" fontSize="16" fontWeight="700" fontFamily="system-ui">
          {score}
        </text>
      </svg>
      <div style={{ fontSize: 11, color: '#475569', marginTop: 3 }}>Priority Score</div>
    </div>
  );
}

export default function SiteDetail() {
  const { viewMode, selectedId } = useDashboard();
  const site = useMemo(() => ENERGY_SITES[selectedId] ?? ENERGY_SITES[0], [selectedId]);

  const roofStyle = site.roof === 'Good'
    ? { bg: 'rgba(16,185,129,.15)', text: '#6EE7B7' }
    : site.roof === 'Fair'
    ? { bg: 'rgba(245,158,11,.15)', text: '#FCD34D' }
    : { bg: 'rgba(239,68,68,.15)', text: '#FCA5A5' };

  const bessKwh = site.bessKwh ?? 750;

  return (
    <div>
      <div style={{
        fontSize: 10, fontWeight: 600, color: '#475569',
        letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 12,
        display: 'flex', alignItems: 'center', gap: 6,
      }}>
        Site Detail —
        <span style={{ color: '#60A5FA', textTransform: 'none', letterSpacing: 0, fontSize: 12, fontWeight: 500 }}>
          {site.name}
        </span>
      </div>

      <div style={{ background: '#131C2E', border: '1px solid #1E293B', borderRadius: 12, padding: 16 }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, minmax(0, 1fr))', gap: 20 }}>

          {/* Column 1: Identity */}
          <div>
            <div style={{ fontSize: 15, fontWeight: 700, marginBottom: 10, lineHeight: 1.3 }}>{site.name}</div>
            <div style={{ display: 'grid', gap: 6 }}>
              <KVItem label="ADDRESS"   value={site.addr}   valueStyle={{ fontSize: 11, color: '#94A3B8' }} />
              <KVItem label="AGENCY"    value={site.agency} />
              <KVItem label="BBL"       value={site.bbl}    valueStyle={{ fontFamily: 'monospace', fontSize: 12, color: '#64748B' }} />
              <div style={{ background: '#0B1120', borderRadius: 6, padding: '8px 10px' }}>
                <div style={{ fontSize: 10, color: '#475569', marginBottom: 2 }}>EJ STATUS</div>
                <span style={{
                  display: 'inline-block', padding: '2px 6px', borderRadius: 20, fontSize: 11, fontWeight: 500,
                  background: site.ej ? 'rgba(16,185,129,.15)' : 'rgba(100,116,139,.15)',
                  color: site.ej ? '#6EE7B7' : '#94A3B8',
                }}>
                  {site.ej ? 'EJ Area' : 'Non-EJ'}
                </span>
              </div>
            </div>
          </div>

          {/* Column 2: Energy Profile */}
          <div>
            <div style={{ fontSize: 10, fontWeight: 600, color: '#475569', letterSpacing: '0.08em', marginBottom: 10 }}>ENERGY PROFILE</div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 6 }}>
              <KVItem label="Monthly Avg"    value={`${site.cons} kWh`} />
              <KVItem label="Peak Demand"    value={`${site.peak} kW`} />
              <KVItem label="Annual Cost"    value={site.cost}         valueStyle={{ color: '#FCA5A5' }} />
              <KVItem label="Solar Potential"value={`${site.solPot} kWh/yr`} valueStyle={{ color: '#FCD34D' }} />
              <div style={{ background: '#0B1120', borderRadius: 6, padding: '8px 10px' }}>
                <div style={{ fontSize: 10, color: '#475569', marginBottom: 2 }}>Roof</div>
                <span style={{ display: 'inline-block', padding: '2px 6px', borderRadius: 20, fontSize: 11, fontWeight: 500, background: roofStyle.bg, color: roofStyle.text }}>
                  {site.roof}
                </span>
              </div>
              <KVItem label="EV Ports"       value={`${site.ev} nearby`} />
            </div>
          </div>

          {/* Column 3: BESS + Waste */}
          <div>
            <div style={{ fontSize: 10, fontWeight: 600, color: '#475569', letterSpacing: '0.08em', marginBottom: 10 }}>BESS RECOMMENDATION</div>
            <ScoreRing score={site.score} />
            <div style={{ display: 'grid', gap: 6 }}>
              <KVItem label="Recommended Capacity" value={`${bessKwh} kWh BESS`} valueStyle={{ color: '#93C5FD' }} />
              <KVItem label="Est. Annual Savings"  value={`${site.savings}/yr`}   valueStyle={{ color: '#6EE7B7' }} />
              <KVItem label="Peak Reduction"       value={`${site.pkRed} kW (${site.pkPct}%)`} />
              <KVItem label="CO₂ Offset"           value={`${site.co2} tons/yr`}  valueStyle={{ color: '#6EE7B7' }} />
            </div>
            <div style={{
              marginTop: 8, background: '#0B1120', borderRadius: 6, padding: 8,
              fontSize: 11, color: '#64748B',
            }}>
              <div style={{ fontSize: 9, color: '#334155', marginBottom: 4, fontWeight: 600, letterSpacing: '0.08em' }}>WASTE CONTEXT</div>
              Refuse: <span style={{ color: '#F59E0B' }}>{site.wasteRef} t/mo</span> · Organic: <span style={{ color: '#10B981' }}>{site.wasteOrg}</span>{' '}
              → <span style={{ color: '#10B981' }}>{site.wasteDivert} t/mo</span> → <span style={{ color: '#10B981' }}>~{site.wasteMWh} MWh/yr</span> biogas
            </div>
          </div>
        </div>

        {/* AI Insight bar */}
        <div style={{
          marginTop: 14, background: 'rgba(139,92,246,.05)',
          border: '1px solid rgba(139,92,246,.2)', borderRadius: 8, padding: 12,
          display: 'flex', alignItems: 'flex-start', gap: 10,
        }}>
          <span style={{
            display: 'inline-block', padding: '2px 6px', borderRadius: 20, fontSize: 11,
            fontWeight: 500, background: 'rgba(139,92,246,.15)', color: '#C4B5FD',
            whiteSpace: 'nowrap', flexShrink: 0,
          }}>
            🤖 AI Insight
          </span>
          <span style={{ fontSize: 12, color: '#94A3B8', lineHeight: 1.6 }}>
            This {site.borough} site{site.ej ? ' sits in an Environmental Justice area with' : ' has'} the borough's highest energy cost.
            The surrounding district produces {site.wasteRef} tons/month of refuse — {site.wasteOrg} organic — with only{' '}
            {site.ej ? '14.2' : '21'}% diversion rate. Recommended: deploy {bessKwh} kWh BESS for peak shaving ({site.savings}/yr savings),
            and partner with Newtown Creek AD facility to process district organics into biogas.
            Combined CO₂ offset: <strong style={{ color: '#10B981' }}>{site.co2} tons/yr</strong>,
            serving residents in {site.ej ? 'an underserved' : 'the ' + site.borough} community.
          </span>
        </div>
      </div>
    </div>
  );
}

'use client';

import { useDashboard } from '../context/DashboardContext';
import { scoreColor } from '../data/sites';

function KVItem({ label, value, valueStyle }) {
  return (
    <div style={{ background: '#F8FAFC', borderRadius: 6, padding: '8px 10px' }}>
      <div style={{ fontSize: 10, color: '#475569', marginBottom: 2 }}>{label}</div>
      <div style={{ fontSize: 13, fontWeight: 600, color: '#0F172A', ...valueStyle }}>{value ?? '—'}</div>
    </div>
  );
}

function ScoreRing({ score, label }) {
  const r = 28;
  const circ = 2 * Math.PI * r;
  const offset = circ * (1 - score / 100);
  const color = scoreColor(score);
  return (
    <div style={{ textAlign: 'center' }}>
      <svg viewBox="0 0 64 64" width={64} height={64} style={{ display: 'block', margin: '0 auto' }}>
        <circle cx="32" cy="32" r={r} fill="none" stroke="#E2E8F0" strokeWidth="6" />
        <circle cx="32" cy="32" r={r} fill="none"
          stroke={color} strokeWidth="6"
          strokeDasharray={circ.toFixed(1)} strokeDashoffset={offset.toFixed(1)}
          strokeLinecap="round" transform="rotate(-90 32 32)"
        />
        <text x="32" y="37" textAnchor="middle" fill="#0F172A" fontSize="14" fontWeight="700" fontFamily="system-ui">{score}</text>
      </svg>
      <div style={{ fontSize: 10, color: '#475569', marginTop: 2 }}>{label}</div>
    </div>
  );
}

function ScoreBar({ label, val, color }) {
  return (
    <div style={{ marginBottom: 8 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 10, color: '#64748B', marginBottom: 3 }}>
        <span>{label}</span><span style={{ color, fontWeight: 700 }}>{val}/100</span>
      </div>
      <div style={{ height: 4, background: '#E2E8F0', borderRadius: 2, overflow: 'hidden' }}>
        <div style={{ height: '100%', width: `${val}%`, background: color, borderRadius: 2, transition: 'width 0.4s ease' }} />
      </div>
    </div>
  );
}

function fmtKwh(n) {
  if (n == null) return '—';
  if (n >= 1e6) return `${(n / 1e6).toFixed(1)}M kWh/yr`;
  if (n >= 1e3) return `${(n / 1e3).toFixed(0)}K kWh/yr`;
  return `${Math.round(n)} kWh/yr`;
}

function fmtUsd(n) {
  if (!n || n === 0) return '—';
  if (n >= 1e6) return `$${(n / 1e6).toFixed(1)}M`;
  return `$${(n / 1e3).toFixed(0)}K`;
}

/** ─── Highlight Building layout ─── */
function HighlightDetail({ data: p }) {
  return (
    <div>
      <div style={{
        fontSize: 10, fontWeight: 600, color: '#475569',
        letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 12,
        display: 'flex', alignItems: 'center', gap: 6,
      }}>
        ★ Highlighted Site —
        <span style={{ color: '#F59E0B', textTransform: 'none', letterSpacing: 0, fontSize: 12, fontWeight: 500 }}>
          {p.site}
        </span>
        <span style={{ background: 'rgba(251,191,36,.15)', color: '#F59E0B', padding: '1px 7px', borderRadius: 20, fontSize: 10, fontWeight: 600, marginLeft: 4 }}>
          Rank #{p.rank}
        </span>
      </div>

      <div style={{ background: '#FFFFFF', border: '1px solid #E2E8F0', borderRadius: 12, padding: 16 }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, minmax(0, 1fr))', gap: 20 }}>

          {/* Identity */}
          <div>
            <div style={{ fontSize: 15, fontWeight: 700, marginBottom: 10, lineHeight: 1.3, color: '#0F172A' }}>{p.site}</div>
            <div style={{ display: 'grid', gap: 6 }}>
              <KVItem label="ADDRESS" value={p.address} valueStyle={{ fontSize: 11, color: '#64748B' }} />
              <KVItem label="AGENCY"  value={p.agency} />
              <KVItem label="BOROUGH" value={p.borough} />
              <div style={{ background: '#F8FAFC', borderRadius: 6, padding: '8px 10px' }}>
                <div style={{ fontSize: 10, color: '#475569', marginBottom: 2 }}>EJ STATUS</div>
                <span style={{
                  display: 'inline-block', padding: '2px 6px', borderRadius: 20, fontSize: 11, fontWeight: 500,
                  background: p.ej ? 'rgba(16,185,129,.15)' : 'rgba(100,116,139,.15)',
                  color: p.ej ? '#059669' : '#64748B',
                }}>
                  {p.ej ? '✅ EJ Area' : 'Non-EJ'}
                </span>
              </div>
            </div>
          </div>

          {/* Score breakdown */}
          <div>
            <div style={{ fontSize: 10, fontWeight: 600, color: '#475569', letterSpacing: '0.08em', marginBottom: 12 }}>XGBoost SCORE BREAKDOWN</div>
            <div style={{ display: 'flex', justifyContent: 'space-around', marginBottom: 14 }}>
              <ScoreRing score={p.energy_score} label="Energy" />
              <ScoreRing score={p.waste_score}  label="Waste"  />
              <ScoreRing score={p.nexus_score}  label="Nexus"  />
            </div>
            <ScoreBar label="Energy Score" val={p.energy_score} color="#3B82F6" />
            <ScoreBar label="Waste Score"  val={p.waste_score}  color="#F59E0B" />
            <ScoreBar label="Nexus Score"  val={p.nexus_score}  color="#8B5CF6" />
          </div>

          {/* BESS Recommendation */}
          <div>
            <div style={{ fontSize: 10, fontWeight: 600, color: '#475569', letterSpacing: '0.08em', marginBottom: 12 }}>BESS RECOMMENDATION</div>
            <div style={{ display: 'grid', gap: 6 }}>
              <KVItem label="Recommended Capacity" value={`${p.bess_kwh} kWh BESS`} valueStyle={{ color: '#3B82F6' }} />
              <KVItem label="Est. Annual Savings"   value={`${fmtUsd(p.savings_usd)}/yr`} valueStyle={{ color: '#059669' }} />
            </div>
            <div style={{
              marginTop: 10, background: 'rgba(59,130,246,.06)',
              border: '1px solid rgba(59,130,246,.2)', borderRadius: 8, padding: '10px 12px',
            }}>
              <div style={{ fontSize: 9, color: '#475569', fontWeight: 600, letterSpacing: '0.08em', marginBottom: 5 }}>TOP RECOMMENDATION</div>
              <div style={{ fontSize: 11, color: '#3B82F6', lineHeight: 1.5 }}>{p.recommendation}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

/** ─── District Building layout ─── */
function BuildingDetail({ data: p }) {
  return (
    <div>
      <div style={{
        fontSize: 10, fontWeight: 600, color: '#475569',
        letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 12,
        display: 'flex', alignItems: 'center', gap: 6,
      }}>
        Building Detail —
        <span style={{ color: '#10B981', textTransform: 'none', letterSpacing: 0, fontSize: 12, fontWeight: 500 }}>
          {p.site || p.address}
        </span>
        <span style={{ background: 'rgba(16,185,129,.15)', color: '#059669', padding: '1px 7px', borderRadius: 20, fontSize: 10, fontWeight: 600, marginLeft: 4 }}>
          District {p.districtCode}
        </span>
      </div>

      <div style={{ background: '#FFFFFF', border: '1px solid #E2E8F0', borderRadius: 12, padding: 16 }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, minmax(0, 1fr))', gap: 20 }}>

          {/* Identity */}
          <div>
            <div style={{ fontSize: 15, fontWeight: 700, marginBottom: 10, lineHeight: 1.3, color: '#0F172A' }}>{p.site || p.address}</div>
            <div style={{ display: 'grid', gap: 6 }}>
              <KVItem label="ADDRESS" value={p.address} valueStyle={{ fontSize: 11, color: '#64748B' }} />
              <KVItem label="AGENCY"  value={p.agency} />
              <KVItem label="DISTRICT" value={p.districtCode} />
              <div style={{ background: '#F8FAFC', borderRadius: 6, padding: '8px 10px' }}>
                <div style={{ fontSize: 10, color: '#475569', marginBottom: 2 }}>EJ STATUS</div>
                <span style={{
                  display: 'inline-block', padding: '2px 6px', borderRadius: 20, fontSize: 11, fontWeight: 500,
                  background: p.ej ? 'rgba(16,185,129,.15)' : 'rgba(100,116,139,.15)',
                  color: p.ej ? '#059669' : '#64748B',
                }}>
                  {p.ej ? '✅ EJ Area' : 'Non-EJ'}
                </span>
              </div>
            </div>
          </div>

          {/* Energy profile */}
          <div>
            <div style={{ fontSize: 10, fontWeight: 600, color: '#475569', letterSpacing: '0.08em', marginBottom: 12 }}>ENERGY PROFILE</div>
            <div style={{ display: 'grid', gap: 6 }}>
              <KVItem label="Solar Potential"   value={fmtKwh(p.solar_kwh_yr)} valueStyle={{ color: '#F59E0B' }} />
              <KVItem label="Est. Annual Cost"  value={fmtUsd(p.annual_cost_usd)} valueStyle={{ color: '#EF4444' }} />
              <KVItem label="GHG Emissions"     value={p.ghg_co2 != null ? `${p.ghg_co2} t CO₂/yr` : '—'} valueStyle={{ color: '#64748B' }} />
            </div>
          </div>

          {/* BESS */}
          <div>
            <div style={{ fontSize: 10, fontWeight: 600, color: '#475569', letterSpacing: '0.08em', marginBottom: 12 }}>BESS RECOMMENDATION</div>
            <div style={{ display: 'grid', gap: 6 }}>
              <KVItem label="Recommended Capacity" value={p.bess_kwh ? `${p.bess_kwh} kWh BESS` : '—'} valueStyle={{ color: '#3B82F6' }} />
              <KVItem label="Est. Annual Savings"  value={p.bess_savings_usd ? `${fmtUsd(p.bess_savings_usd)}/yr` : '—'} valueStyle={{ color: '#059669' }} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

/** ─── District layout ─── */
function DistrictDetail({ data: p }) {
  return (
    <div>
      <div style={{
        fontSize: 10, fontWeight: 600, color: '#475569',
        letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 12,
        display: 'flex', alignItems: 'center', gap: 6,
      }}>
        District Detail —
        <span style={{ color: '#EAB308', textTransform: 'none', letterSpacing: 0, fontSize: 12, fontWeight: 500 }}>
          {p.district || p.code}
        </span>
        <span style={{ background: 'rgba(234,179,8,.15)', color: '#CA8A04', padding: '1px 7px', borderRadius: 20, fontSize: 10, fontWeight: 600, marginLeft: 4 }}>
          Rank #{p.rank}
        </span>
      </div>

      <div style={{ background: '#FFFFFF', border: '1px solid #E2E8F0', borderRadius: 12, padding: 16 }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, minmax(0, 1fr))', gap: 20 }}>

          {/* Identity */}
          <div>
            <div style={{ fontSize: 15, fontWeight: 700, marginBottom: 10, lineHeight: 1.3, color: '#0F172A' }}>{p.district || p.code}</div>
            <div style={{ display: 'grid', gap: 6 }}>
              <KVItem label="DISTRICT CODE" value={p.code} />
              <KVItem label="BOROUGH"       value={p.borough} />
              <div style={{ background: '#F8FAFC', borderRadius: 6, padding: '8px 10px' }}>
                <div style={{ fontSize: 10, color: '#475569', marginBottom: 2 }}>EJ COVERAGE</div>
                <span style={{
                  display: 'inline-block', padding: '2px 6px', borderRadius: 20, fontSize: 11, fontWeight: 500,
                  background: p.pct_ej > 20 ? 'rgba(139,92,246,.15)' : 'rgba(100,116,139,.15)',
                  color: p.pct_ej > 20 ? '#7C3AED' : '#64748B',
                }}>
                  {p.pct_ej}% EJ Buildings
                </span>
              </div>
            </div>
          </div>

          {/* Solar potential */}
          <div>
            <div style={{ fontSize: 10, fontWeight: 600, color: '#475569', letterSpacing: '0.08em', marginBottom: 12 }}>SOLAR POTENTIAL</div>
            <div style={{ display: 'grid', gap: 6 }}>
              <KVItem label="Total Solar Potential" value={fmtKwh(p.solar_kwh_yr)} valueStyle={{ color: '#F59E0B' }} />
              <KVItem label="Total Buildings"       value={p.buildings} />
              <KVItem label="Solar-Ready Buildings" value={p.solar_ready} valueStyle={{ color: '#059669' }} />
            </div>
          </div>

          {/* BESS savings */}
          <div>
            <div style={{ fontSize: 10, fontWeight: 600, color: '#475569', letterSpacing: '0.08em', marginBottom: 12 }}>BESS DISTRICT SAVINGS</div>
            <div style={{ display: 'grid', gap: 6 }}>
              <KVItem label="Total BESS Savings" value={fmtUsd(p.bess_savings_usd) + '/yr'} valueStyle={{ color: '#059669' }} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

/** ─── Placeholder ─── */
function Placeholder() {
  return (
    <div style={{
      background: '#FFFFFF', border: '1px solid #E2E8F0', borderRadius: 12, padding: '28px 20px',
      textAlign: 'center', color: '#94A3B8', fontSize: 13,
    }}>
      Click a building dot <span style={{ color: '#10B981' }}>●</span>, district centroid <span style={{ color: '#EAB308' }}>◎</span>, or highlighted star <span style={{ color: '#FBBF24' }}>★</span> on the map to see details here.
    </div>
  );
}

export default function SiteDetail() {
  const { selectedItem } = useDashboard();

  const sectionLabel = (
    <div style={{
      fontSize: 10, fontWeight: 600, color: '#475569',
      letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 12,
    }}>
      Site Detail
    </div>
  );

  if (!selectedItem) {
    return (
      <div>
        {sectionLabel}
        <Placeholder />
      </div>
    );
  }

  const { type, data } = selectedItem;

  if (type === 'highlight') return <HighlightDetail data={data} />;
  if (type === 'building')  return <BuildingDetail  data={data} />;
  if (type === 'district')  return <DistrictDetail  data={data} />;

  return (
    <div>
      {sectionLabel}
      <Placeholder />
    </div>
  );
}

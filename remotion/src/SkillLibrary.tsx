import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';

type Skill = {
  name: string;
  checks: string[];
  color: string;
  soft: string;
};

const BLUE = '#2456b3';
const VIOLET = '#7b5cf5';
const GREEN = '#25814f';

const SKILLS: Skill[] = [
  {
    name: 'RenderQualityInspector',
    checks: ['aesthetic quality', 'imaging quality', 'flicker', 'motion smoothness', 'artifact/readability gate'],
    color: BLUE,
    soft: '#e8eef9',
  },
  {
    name: 'PhysicalPlausibilityInspector',
    checks: ['support/contact', 'object integrity', 'scale/perspective', 'motion feasibility', 'judgeability gate'],
    color: BLUE,
    soft: '#e8eef9',
  },
  {
    name: 'ViewpointTrajectoryVerifier',
    checks: ['camera-path adherence', 'navigation consistency', 'layout/view recovery', 'return-trigger support'],
    color: VIOLET,
    soft: '#efeafd',
  },
  {
    name: 'IntentionalChangeVerifier',
    checks: ['semantic accuracy', 'target accuracy', 'specificity', 'preservation diagnostics'],
    color: VIOLET,
    soft: '#efeafd',
  },
  {
    name: 'PhysicalResponseVerifier',
    checks: ['target motion energy', 'control-region motion', 'response ratio', 'optional VLM response'],
    color: VIOLET,
    soft: '#efeafd',
  },
  {
    name: 'PhysicalDynamicsVerifier',
    checks: ['simulator/analytic validators', 'trajectory constraints', 'process consistency', 'task-specific kinematics'],
    color: VIOLET,
    soft: '#efeafd',
  },
  {
    name: 'DriftDegradationAnalyzer',
    checks: ['chunk quality curve', 'degradation drop', 'half-life', 'identity/layout drift diagnostics'],
    color: GREEN,
    soft: '#e8f3ec',
  },
  {
    name: 'ReturnConsistencyVerifier',
    checks: ['return trigger', 'entity consistency', 'environment consistency', 'render consistency'],
    color: GREEN,
    soft: '#e8f3ec',
  },
  {
    name: 'OffscreenEvolutionVerifier',
    checks: ['reappearance', 'expected evolution', 'relation continuity', 'freeze/reset diagnostics'],
    color: GREEN,
    soft: '#e8f3ec',
  },
];

// Geometry (canvas 1920 x 900)
const HUB = {x: 70, y: 372, w: 320, h: 156};
const HUB_ANCHOR = {x: HUB.x + HUB.w, y: HUB.y + HUB.h / 2};
const RAIL_X = 432;
const CARD_X = 474;
const CARD_W = 442;
const CARD_H = 62;
const CHIPS_X = 964;
const CHIPS_W = 900;
const rowY = (i: number) => 118 + i * 83;

const ROW_START = (i: number) => 34 + i * 12;

const cubicPoint = (t: number, p0: number[], c1: number[], c2: number[], p1: number[]) => {
  const u = 1 - t;
  const x = u * u * u * p0[0] + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0] + t * t * t * p1[0];
  const y = u * u * u * p0[1] + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1] + t * t * t * p1[1];
  return {x, y};
};

const connectorPoints = (i: number) => {
  const p0 = [HUB_ANCHOR.x, HUB_ANCHOR.y];
  const c1 = [RAIL_X, HUB_ANCHOR.y];
  const c2 = [RAIL_X, rowY(i)];
  const p1 = [CARD_X, rowY(i)];
  return {p0, c1, c2, p1};
};

const connectorPath = (i: number) => {
  const {p0, c1, c2, p1} = connectorPoints(i);
  return `M ${p0[0]} ${p0[1]} C ${c1[0]} ${c1[1]}, ${c2[0]} ${c2[1]}, ${p1[0]} ${p1[1]}`;
};

export const SkillLibrary: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const enter = (start: number, durationOverride?: number) =>
    spring({
      frame: frame - start,
      fps,
      config: {damping: 15, stiffness: 130, mass: 0.9},
      durationInFrames: durationOverride,
    });

  const fadeIn = (start: number, len: number) =>
    interpolate(frame, [start, start + len], [0, 1], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    });

  const hubIn = enter(4);
  const railGrow = interpolate(frame, [14, 44], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Ambient pulses flowing along connectors after the build-in.
  const PULSE_START = 178;
  const PULSE_PERIOD = 74;
  const pulseGlobal = interpolate(frame, [PULSE_START, PULSE_START + 20, 312, 346], [0, 1, 1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill
      style={{
        background: 'linear-gradient(155deg, #f8f6fa 0%, #f1eef5 55%, #eae6f1 100%)',
        fontFamily:
          '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
      }}
    >
      {/* faint dot grid */}
      <AbsoluteFill
        style={{
          backgroundImage: 'radial-gradient(rgba(61, 54, 84, 0.10) 1.2px, transparent 1.2px)',
          backgroundSize: '34px 34px',
          opacity: fadeIn(0, 20) * 0.7,
        }}
      />
      {/* soft color glows */}
      <AbsoluteFill
        style={{
          opacity: fadeIn(0, 30),
          background:
            'radial-gradient(620px 420px at 12% 20%, rgba(36, 86, 179, 0.07), transparent 70%),' +
            'radial-gradient(700px 500px at 55% 55%, rgba(123, 92, 245, 0.07), transparent 70%),' +
            'radial-gradient(620px 420px at 20% 88%, rgba(37, 129, 79, 0.06), transparent 70%)',
        }}
      />

      {/* connectors + rail + pulses */}
      <svg width={1920} height={900} style={{position: 'absolute', inset: 0}}>
        <defs>
          <linearGradient id="rail" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={BLUE} />
            <stop offset="20%" stopColor={BLUE} />
            <stop offset="30%" stopColor={VIOLET} />
            <stop offset="62%" stopColor={VIOLET} />
            <stop offset="72%" stopColor={GREEN} />
            <stop offset="100%" stopColor={GREEN} />
          </linearGradient>
        </defs>

        {/* vertical rail */}
        <rect
          x={RAIL_X - 3}
          y={rowY(0) - 34 + (1 - railGrow) * ((rowY(8) + 34 - (rowY(0) - 34)) / 2)}
          width={6}
          height={(rowY(8) + 34 - (rowY(0) - 34)) * railGrow}
          rx={3}
          fill="url(#rail)"
          opacity={0.9}
        />

        {SKILLS.map((skill, i) => {
          const start = ROW_START(i);
          const draw = interpolate(frame, [start, start + 20], [0, 1], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          });
          if (draw === 0) return null;
          return (
            <path
              key={skill.name}
              d={connectorPath(i)}
              pathLength={1}
              stroke={skill.color}
              strokeOpacity={0.45}
              strokeWidth={2.6}
              fill="none"
              strokeDasharray={1}
              strokeDashoffset={1 - draw}
              strokeLinecap="round"
            />
          );
        })}

        {/* travelling pulses */}
        {pulseGlobal > 0.01 &&
          SKILLS.map((skill, i) => {
            const local = (frame - PULSE_START + i * 9) % PULSE_PERIOD;
            const t = local / (PULSE_PERIOD * 0.62);
            if (t < 0 || t > 1) return null;
            const {p0, c1, c2, p1} = connectorPoints(i);
            const pt = cubicPoint(t, p0, c1, c2, p1);
            const edgeFade = Math.sin(Math.PI * t);
            const o = pulseGlobal * edgeFade;
            return (
              <g key={`pulse-${skill.name}`}>
                <circle cx={pt.x} cy={pt.y} r={11} fill={skill.color} opacity={o * 0.18} />
                <circle cx={pt.x} cy={pt.y} r={4.5} fill={skill.color} opacity={o * 0.9} />
              </g>
            );
          })}

        {/* arrows card -> chips */}
        {SKILLS.map((skill, i) => {
          const start = ROW_START(i) + 14;
          const draw = interpolate(frame, [start, start + 12], [0, 1], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          });
          if (draw === 0) return null;
          const y = rowY(i);
          const x0 = CARD_X + CARD_W + 6;
          const x1 = x0 + 32 * draw;
          return (
            <g key={`arrow-${skill.name}`} opacity={draw}>
              <line x1={x0} y1={y} x2={x1} y2={y} stroke="#b6b0bd" strokeWidth={2.4} strokeLinecap="round" />
              <path
                d={`M ${x1 + 8} ${y} l -9 -5.5 l 0 11 z`}
                fill="#b6b0bd"
                opacity={draw > 0.85 ? 1 : 0}
              />
            </g>
          );
        })}
      </svg>

      {/* hub card */}
      <div
        style={{
          position: 'absolute',
          left: HUB.x,
          top: HUB.y,
          width: HUB.w,
          height: HUB.h,
          borderRadius: 18,
          background: 'linear-gradient(150deg, #1d1a26 0%, #17161c 60%, #221c31 100%)',
          boxShadow: '0 24px 60px rgba(11, 9, 18, 0.28), inset 0 0 0 1px rgba(167, 139, 250, 0.22)',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          padding: '0 30px',
          opacity: Math.min(1, hubIn * 1.4),
          transform: `scale(${0.9 + 0.1 * hubIn}) translateY(${(1 - hubIn) * 14}px)`,
        }}
      >
        <div
          style={{
            fontSize: 14,
            letterSpacing: 3,
            textTransform: 'uppercase',
            color: '#a78bfa',
            fontWeight: 600,
            marginBottom: 10,
          }}
        >
          HarnessEval-W
        </div>
        <div
          style={{
            fontFamily: 'Georgia, "Times New Roman", serif',
            fontSize: 37,
            fontWeight: 700,
            color: '#f7f5f9',
            lineHeight: 1.08,
          }}
        >
          Skill Library
        </div>
        <div style={{fontSize: 15, color: 'rgba(247, 245, 249, 0.55)', marginTop: 10}}>
          9 evaluation skills · skill-orchestrated checks
        </div>
      </div>

      {/* rows */}
      {SKILLS.map((skill, i) => {
        const start = ROW_START(i);
        const cardIn = enter(start + 8);
        const cardOpacity = fadeIn(start + 8, 10);
        const y = rowY(i);
        return (
          <div key={skill.name}>
            {/* skill card */}
            <div
              style={{
                position: 'absolute',
                left: CARD_X,
                top: y - CARD_H / 2,
                width: CARD_W,
                height: CARD_H,
                borderRadius: 12,
                background: '#ffffff',
                border: '1px solid #d8d5dd',
                borderLeft: `5px solid ${skill.color}`,
                boxShadow: '0 10px 26px rgba(23, 22, 28, 0.07)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '0 20px 0 22px',
                opacity: cardOpacity,
                transform: `translateY(${(1 - cardIn) * 16}px) scale(${0.96 + 0.04 * cardIn})`,
              }}
            >
              <span
                style={{
                  fontFamily: 'Georgia, "Times New Roman", serif',
                  fontSize: 24.5,
                  fontWeight: 700,
                  color: '#17161c',
                  whiteSpace: 'nowrap',
                }}
              >
                {skill.name}
              </span>
              <span
                style={{
                  fontFamily: '"SF Mono", ui-monospace, Menlo, monospace',
                  fontSize: 15,
                  color: '#b6b0bd',
                  fontWeight: 500,
                }}
              >
                {String(i + 1).padStart(2, '0')}
              </span>
            </div>

            {/* capability chips */}
            <div
              style={{
                position: 'absolute',
                left: CHIPS_X,
                top: y - CARD_H / 2 - 4,
                width: CHIPS_W,
                height: CARD_H + 8,
                display: 'flex',
                alignItems: 'center',
                flexWrap: 'wrap',
                gap: '8px 10px',
              }}
            >
              {skill.checks.map((check, j) => {
                const chipStart = start + 20 + j * 3;
                const chipIn = fadeIn(chipStart, 10);
                return (
                  <span
                    key={check}
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: 9,
                      padding: '7.5px 15px',
                      borderRadius: 999,
                      background: 'rgba(255, 255, 255, 0.85)',
                      border: '1px solid #d8d5dd',
                      fontSize: 16.5,
                      color: '#3d3654',
                      whiteSpace: 'nowrap',
                      opacity: chipIn,
                      transform: `translateX(${(1 - chipIn) * 14}px)`,
                    }}
                  >
                    <span
                      style={{
                        width: 7,
                        height: 7,
                        borderRadius: 999,
                        background: skill.color,
                        flexShrink: 0,
                      }}
                    />
                    {check}
                  </span>
                );
              })}
            </div>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

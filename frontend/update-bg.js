const fs = require('fs');

// Update DayPredictionCard.tsx
let f1 = fs.readFileSync('src/components/prediction/DayPredictionCard.tsx', 'utf8');

f1 = f1.replace(
  /\} from "\.\.\/\.\.\/utils\/predictionI18n";/,
  } from "../../utils/predictionI18n";\nimport { AstroMoodBackground } from "../astro/AstroMoodBackground";\nimport type { ZodiacSign } from "../astro/zodiacPatterns";
);

f1 = f1.replace(
  /interface Props \{\n  prediction: DailyPredictionResponse;\n  lang: Lang;\n\}/,
  interface Props {\n  prediction: DailyPredictionResponse;\n  lang: Lang;\n  astroBackgroundProps?: {\n    sign: ZodiacSign;\n    userId: string;\n    dayScore: number;\n    dateKey: string;\n  };\n}
);

f1 = f1.replace(
  /export const DayPredictionCard: React\.FC<Props> = \(\{ prediction, lang \}\) => \{/,
  xport const DayPredictionCard: React.FC<Props> = ({ prediction, lang, astroBackgroundProps }) => {
);

const originalCardStart = <div className="panel hero-card" style={{ marginBottom: "1.5rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1rem" }}>
        <div>
          <h2 style={{ margin: 0, fontSize: "1.5rem" }}>{formattedDate}</h2>
          <span style={{ 
            display: "inline-block", 
            marginTop: "0.5rem",
            padding: "0.25rem 0.75rem", 
            borderRadius: "1rem", 
            backgroundColor: toneColor, 
            color: "white",
            fontSize: "0.875rem",
            fontWeight: "bold"
          }}>
            {toneLabel}
          </span>
        </div>
      </div>

      <p style={{ fontSize: "1.125rem", lineHeight: "1.6", color: "var(--text-1)" }}>;

const newCardStart = <div className="panel hero-card day-prediction-card">
      {astroBackgroundProps ? (
        <div className="day-prediction-card__header-bg-wrapper">
          <AstroMoodBackground
            sign={astroBackgroundProps.sign}
            userId={astroBackgroundProps.userId}
            dateKey={astroBackgroundProps.dateKey}
            dayScore={astroBackgroundProps.dayScore}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1rem" }}>
              <div style={{ position: "relative", zIndex: 10 }}>
                <h2 style={{ margin: 0, fontSize: "1.5rem" }}>{formattedDate}</h2>
                <span style={{ 
                  display: "inline-block", 
                  marginTop: "0.5rem",
                  padding: "0.25rem 0.75rem", 
                  borderRadius: "1rem", 
                  backgroundColor: toneColor, 
                  color: "white",
                  fontSize: "0.875rem",
                  fontWeight: "bold"
                }}>
                  {toneLabel}
                </span>
              </div>
            </div>
          </AstroMoodBackground>
        </div>
      ) : (
        <div className="day-prediction-card__header-fallback">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1rem" }}>
            <div>
              <h2 style={{ margin: 0, fontSize: "1.5rem" }}>{formattedDate}</h2>
              <span style={{ 
                display: "inline-block", 
                marginTop: "0.5rem",
                padding: "0.25rem 0.75rem", 
                borderRadius: "1rem", 
                backgroundColor: toneColor, 
                color: "white",
                fontSize: "0.875rem",
                fontWeight: "bold"
              }}>
                {toneLabel}
              </span>
            </div>
          </div>
        </div>
      )}

      <div className="day-prediction-card__body">
        <p style={{ fontSize: "1.125rem", lineHeight: "1.6", color: "var(--text-1)" }}>;

f1 = f1.replace(originalCardStart, newCardStart);

f1 = f1.replace(
  /    <\/div>\n  \);\n\};\n/g,
        </div>\n    </div>\n  );\n};\n
);

fs.writeFileSync('src/components/prediction/DayPredictionCard.tsx', f1);

// Update DailyHoroscopePage.tsx
let f2 = fs.readFileSync('src/pages/DailyHoroscopePage.tsx', 'utf8');

f2 = f2.replace(
  /<div className="hero-card-astro-bg-wrapper">\n\s*<AstroMoodBackground\n\s*sign=\{sign\}\n\s*userId=\{user\?\.id \|\| 'anonymous'\}\n\s*dateKey=\{prediction\.meta\.date_local\}\n\s*dayScore=\{dayScore\}\n\s*>\n\s*<DayPredictionCard prediction=\{prediction\} lang=\{lang\} \/>\n\s*<\/AstroMoodBackground>\n\s*<\/div>/g,
  <DayPredictionCard\n            prediction={prediction}\n            lang={lang}\n            astroBackgroundProps={{\n              sign,\n              userId: user?.id || 'anonymous',\n              dateKey: prediction.meta.date_local,\n              dayScore\n            }}\n          />
);

fs.writeFileSync('src/pages/DailyHoroscopePage.tsx', f2);

// Update App.css
let f3 = fs.readFileSync('src/App.css', 'utf8');

f3 = f3.replace(
  /\/\* === Horoscope Page Modifications === \*\/\n\.hero-card-astro-bg-wrapper \{\n  margin-bottom: 1\.5rem;\n  border-radius: 28px;\n  overflow: hidden;\n  border: 1px solid var\(--line\);\n  position: relative;\n\}\n\n\.hero-card-astro-bg-wrapper \.astro-mood-background__content \{\n  padding: 0;\n\}\n\n\.hero-card-astro-bg-wrapper \.panel\.hero-card \{\n  background: transparent !important;\n  border: none !important;\n  box-shadow: none !important;\n  margin-bottom: 0 !important;\n  position: relative;\n  z-index: 2;\n\}/g,
  /* === Horoscope Page Modifications === */
.day-prediction-card {
  padding: 0;
  overflow: hidden;
  margin-bottom: 1.5rem;
}

.day-prediction-card__header-bg-wrapper .astro-mood-background {
  border-radius: 0;
  border-bottom: 1px solid var(--line);
}

.day-prediction-card__header-bg-wrapper .astro-mood-background__content {
  padding: 1.5rem;
  min-height: auto;
}

.day-prediction-card__header-fallback {
  padding: 1.5rem 1.5rem 0 1.5rem;
}

.day-prediction-card__body {
  padding: 0 1.5rem 1.5rem 1.5rem;
}

.day-prediction-card__header-bg-wrapper + .day-prediction-card__body {
  padding-top: 1.5rem;
}

);

fs.writeFileSync('src/App.css', f3);

console.log('Update script successful');

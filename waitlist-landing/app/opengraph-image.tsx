import { ImageResponse } from "next/og";
import { site } from "@/lib/site";

export const runtime = "edge";
export const alt = `${site.brandName} — ${site.tagline}`;
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function OgImage() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          background: "#FBF9F4",
          color: "#17383B",
          padding: "72px 80px",
          fontFamily: "Georgia, serif",
        }}
      >
        <div
          style={{
            fontSize: 28,
            letterSpacing: "0.25em",
            textTransform: "uppercase",
            color: "#A05F10",
          }}
        >
          {site.brandName}
        </div>
        <div style={{ display: "flex", flexDirection: "column" }}>
          <div style={{ fontSize: 72, lineHeight: 1.1, maxWidth: 900 }}>
            NZ&apos;s batch-tested NMN.
          </div>
          <div
            style={{
              fontSize: 32,
              marginTop: 28,
              color: "#A05F10",
            }}
          >
            Founding members get 30% off.
          </div>
        </div>
        <div style={{ fontSize: 22, color: "#84908D" }}>
          Dietary supplement · Independently tested in NZ labs
        </div>
      </div>
    ),
    size
  );
}

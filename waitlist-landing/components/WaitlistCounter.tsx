"use client";

import { useEffect, useState } from "react";
import { site } from "@/lib/site";

/**
 * Shows the live founding-list size. Reads the real count from the API;
 * the API applies the display floor so the number never reads as empty.
 */
export default function WaitlistCounter() {
  const [count, setCount] = useState<number>(site.waitlistFloor);

  useEffect(() => {
    let cancelled = false;
    fetch("/api/waitlist-count")
      .then((res) => (res.ok ? res.json() : null))
      .then((json) => {
        if (!cancelled && json && typeof json.count === "number") {
          setCount(json.count);
        }
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <p className="text-sm text-stone-mid">
      <span className="font-medium text-ink">{count.toLocaleString()}</span>{" "}
      people on the founding list
    </p>
  );
}

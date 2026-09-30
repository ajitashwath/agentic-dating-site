"use client";

import { useEffect, useState } from "react";

// Portraits are sized in pixels, so phones need a smaller size than a JS-free media query can give.
export function useNarrow() {
  const [narrow, setNarrow] = useState(false);
  useEffect(() => {
    const check = () => setNarrow(window.innerWidth < 640);
    check();
    window.addEventListener("resize", check);
    return () => window.removeEventListener("resize", check);
  }, []);
  return narrow;
}

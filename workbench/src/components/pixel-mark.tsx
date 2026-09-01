const PIXEL_PATTERN = [
  "n.....n",
  "v.....v",
  "v.....v",
  ".v...v.",
  ".v...v.",
  "..v.v..",
  "...v...",
];

export function PixelMark({ large = false, className = "" }: { large?: boolean; className?: string }) {
  return (
    <span className={`pixel-mark${large ? " large" : ""}${className ? ` ${className}` : ""}`} aria-hidden="true">
      {PIXEL_PATTERN.flatMap((row, rowIndex) =>
        [...row].map((pixel, columnIndex) => (
          <i
            className={`pixel-cell ${pixel === "v" ? "core" : pixel === "n" ? "node" : "empty"}`}
            key={`${rowIndex}-${columnIndex}`}
          />
        )),
      )}
    </span>
  );
}

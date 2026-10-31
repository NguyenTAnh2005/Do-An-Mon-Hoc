// src/utils/format.js

// "2026-10-31" → "31/10" — cho nhãn trục X
export const formatDateShort = (iso) => {
  if (!iso) {
    return "";
  }
  const parts = iso.split("-");
  if (parts.length !== 3) {
    return iso;
  }
  return `${parts[2]}/${parts[1]}`;
};

// "2026-10-31" → "31/10/2026" — cho tooltip
export const formatDateFull = (iso) => {
  if (!iso) {
    return "";
  }
  const parts = iso.split("-");
  if (parts.length !== 3) {
    return iso;
  }
  return `${parts[2]}/${parts[1]}/${parts[0]}`;
};
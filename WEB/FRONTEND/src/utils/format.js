// "2026-10-31" → "31/10" — cho nhãn trục X
export const formatDateShort = (iso) => {
  if (!iso) return "";
  const parts = iso.split("-");
  if (parts.length !== 3) return iso;
  return `${parts[2]}/${parts[1]}`;
};

// "2026-10-31" → "31/10/2026" — cho tooltip
export const formatDateFull = (iso) => {
  if (!iso) return "";
  const parts = iso.split("-");
  if (parts.length !== 3) return iso;
  return `${parts[2]}/${parts[1]}/${parts[0]}`;
};

// Điều hướng về trang login — dùng ở interceptor 401 của manualConfig
export const navigateLogIn = () => {
  if (window.location.pathname !== "/log-in") {
    window.location.href = "/log-in";
  }
};
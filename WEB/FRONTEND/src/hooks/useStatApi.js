import { useEffect, useState } from "react";

// fetcher phải là hàm ổn định (import module hoặc useCallback),
// không truyền arrow inline — tránh refetch mỗi lần render.
export const useStatApi = (fetcher) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    const run = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetcher();
        if (!cancelled) {
          setData(res);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    run();

    return () => {
      cancelled = true;
    };
  }, [fetcher]);

  return { data, loading, error };
};
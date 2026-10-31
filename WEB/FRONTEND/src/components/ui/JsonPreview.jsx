// src/components/ui/JsonPreview.jsx
import clsx from "clsx";
import { baseText, metaLabel } from "../../utils/style";

export const JsonPreview = ({ data }) => {
  return (
    <pre
      className={clsx(
        "overflow-x-auto rounded-lg p-3",
        "bg-light-bg dark:bg-dark-bg",
        baseText,
        metaLabel
      )}
    >
      {JSON.stringify(data, null, 2)}
    </pre>
  );
};
import { useEffect, useState } from "react";

export default function Toast({
  message,
  type = "info",
  onClose,
}: {
  message: string;
  type?: "info" | "error" | "success";
  onClose: () => void;
}) {
  const [open, setOpen] = useState(true);
  useEffect(() => {
    const t = setTimeout(() => {
      setOpen(false);
      onClose();
    }, 3000);
    return () => clearTimeout(t);
  }, []);
  if (!open) return null;
  const color =
    type === "error"
      ? "bg-red-100 text-red-800 border-red-300"
      : type === "success"
        ? "bg-green-100 text-green-800 border-green-300"
        : "bg-blue-100 text-blue-800 border-blue-300";
  return (
    <div
      className={`fixed right-4 bottom-4 border rounded-lg px-3 py-2 text-sm shadow ${color}`}
    >
      {message}
    </div>
  );
}

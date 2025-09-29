import { env } from "@/config/env";
import { DISCLAIMER } from "@/utils/constants";

export default function Account() {
  const userId = env.demoUserId;
  return (
    <section className="space-y-4">
      <h1 className="text-xl font-semibold">Account</h1>
      <div className="card p-4 space-y-2">
        <div className="text-sm">
          User ID (from <code>VITE_DEMO_USER_ID</code>):{" "}
          <span className="badge border-gray-300 ml-1">
            {userId || "NOT SET"}
          </span>
        </div>
        <div className="text-xs text-gray-600">{DISCLAIMER}</div>
      </div>
      {!userId && (
        <div className="text-sm text-red-700">
          Set VITE_DEMO_USER_ID in your environment to use authenticated routes.
        </div>
      )}
    </section>
  );
}

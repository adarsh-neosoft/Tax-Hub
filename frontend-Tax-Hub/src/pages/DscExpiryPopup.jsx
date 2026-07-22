import { useEffect, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { api } from "iron-stack-ui";

const styles = {
  overlay: {
    position: "fixed",
    inset: 0,
    zIndex: 9999,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    background: "rgba(0,0,0,0.5)",
    padding: "1rem",
  },
  card: {
    position: "relative",
    width: "100%",
    maxWidth: "48rem",
    maxHeight: "85vh",
    display: "flex",
    flexDirection: "column",
    background: "#fff",
    borderRadius: "0.75rem",
    boxShadow: "0 20px 60px rgba(0,0,0,0.3)",
    overflow: "hidden",
  },
  header: {
    background: "#f59e0b",
    padding: "1rem 1.25rem",
    display: "flex",
    alignItems: "center",
    gap: "0.75rem",
    flexShrink: 0,
  },
  iconCircle: {
    background: "rgba(255,255,255,0.2)",
    borderRadius: "50%",
    padding: "0.5rem",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    flexShrink: 0,
  },
  headerText: { flex: 1 },
  title: { color: "#fff", fontSize: "1.125rem", fontWeight: 700, margin: 0, lineHeight: 1.4 },
  subtitle: { color: "rgba(255,255,255,0.85)", fontSize: "0.875rem", margin: 0, marginTop: "0.125rem" },
  closeBtn: {
    background: "none",
    border: "none",
    color: "rgba(255,255,255,0.7)",
    cursor: "pointer",
    padding: "0.25rem",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    transition: "color 0.15s",
  },
  scrollBody: {
    padding: "1.25rem",
    overflowY: "auto",
    flex: 1,
  },
  infoBar: {
    background: "#fffbeb",
    border: "1px solid #fde68a",
    borderRadius: "0.5rem",
    padding: "0.75rem 1rem",
    marginBottom: "1rem",
    fontSize: "0.875rem",
    color: "#92400e",
  },
  table: {
    width: "100%",
    borderCollapse: "collapse",
    fontSize: "0.875rem",
  },
  th: {
    textAlign: "left",
    padding: "0.625rem 0.75rem",
    borderBottom: "2px solid #e5e7eb",
    color: "#374151",
    fontWeight: 600,
    fontSize: "0.8rem",
    textTransform: "uppercase",
    letterSpacing: "0.05em",
    background: "#f9fafb",
    whiteSpace: "nowrap",
  },
  td: {
    padding: "0.625rem 0.75rem",
    borderBottom: "1px solid #f3f4f6",
    color: "#1f2937",
    verticalAlign: "middle",
  },
  rowHover: {
    transition: "background 0.1s",
  },
  expiryBadge: {
    display: "inline-flex",
    alignItems: "center",
    gap: "0.25rem",
    padding: "0.2rem 0.5rem",
    borderRadius: "9999px",
    fontSize: "0.75rem",
    fontWeight: 500,
    whiteSpace: "nowrap",
  },
  radioGroup: {
    display: "flex",
    gap: "0.75rem",
    alignItems: "center",
    justifyContent: "center",
  },
  radioLabel: {
    display: "flex",
    alignItems: "center",
    gap: "0.25rem",
    cursor: "pointer",
    fontSize: "0.8rem",
    fontWeight: 500,
    padding: "0.25rem 0.5rem",
    borderRadius: "0.375rem",
    transition: "all 0.15s",
  },
  radioYes: { color: "#047857" },
  radioNo: { color: "#b91c1c" },
  emptyYes: { color: "#6b7280" },
  emptyNo: { color: "#6b7280" },
  inputRadio: {
    accentColor: "#059669",
    cursor: "pointer",
  },
  inputRadioRed: {
    accentColor: "#dc2626",
    cursor: "pointer",
  },
  footer: {
    borderTop: "1px solid #e5e7eb",
    padding: "1rem 1.25rem",
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    flexShrink: 0,
    background: "#f9fafb",
  },
  footerInfo: {
    fontSize: "0.8rem",
    color: "#6b7280",
    margin: 0,
  },
  submitBtn: {
    display: "flex",
    alignItems: "center",
    gap: "0.5rem",
    padding: "0.625rem 1.5rem",
    borderRadius: "0.5rem",
    border: "none",
    background: "#059669",
    color: "#fff",
    fontSize: "0.9rem",
    fontWeight: 600,
    cursor: "pointer",
    transition: "all 0.15s",
  },
};

function SpinnerIcon({ size = 20 }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      style={{ animation: "spin 1s linear infinite" }}
    >
      <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" opacity="0.3" />
      <path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
    </svg>
  );
}

function calcDaysLeft(toDate) {
  if (!toDate) return null;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const expiry = new Date(toDate);
  expiry.setHours(0, 0, 0, 0);
  const diff = Math.ceil((expiry - today) / (1000 * 60 * 60 * 24));
  return diff;
}

export default function DscExpiryPopup() {
  const queryClient = useQueryClient();
  const [isVisible, setIsVisible] = useState(true);
  const [selections, setSelections] = useState({}); // { [id]: true/false }

  const { data: expiringDscs = [], isLoading } = useQuery({
    queryKey: ["dsc-expiring-soon"],
    queryFn: async () => {
      const response = await api.get("/registration/dsctracker/expiring-soon/");
      return response.data;
    },
    refetchOnWindowFocus: false,
    staleTime: 60000,
  });

  const mutation = useMutation({
    mutationFn: (updates) =>
      api.post("/registration/dsctracker/batch-update-new-dsc-prepared/", { updates }),
    onSuccess: (response) => {
      const { success, errors } = response.data;
      const successCount = success.length;
      const errorCount = errors.length;

      if (successCount > 0) {
        const yesCount = success.filter((s) => s.new_dsc_prepared === true).length;
        const noCount = success.filter((s) => s.new_dsc_prepared === false).length;

        let msg = `Updated ${successCount} DSC(s).`;
        if (yesCount > 0) msg += ` ${yesCount} marked as ready (no reminders).`;
        if (noCount > 0) msg += ` ${noCount} marked as not ready (weekly reminders will start).`;
        toast.success(msg);
      }

      if (errorCount > 0) {
        toast.error(`${errorCount} record(s) failed to update.`);
      }

      queryClient.invalidateQueries({ queryKey: ["dsc-expiring-soon"] });
      queryClient.invalidateQueries({ queryKey: ["dsctracker"] });
      setIsVisible(false);
    },
    onError: () => {
      toast.error("Failed to submit. Please try again.");
    },
  });

  const handleSelection = (id, value) => {
    setSelections((prev) => ({ ...prev, [id]: value }));
  };

  // Clear selections when data loads
  useEffect(() => {
    if (expiringDscs.length > 0) {
      setIsVisible(true);
    }
  }, [expiringDscs.length]);

  const handleSubmit = () => {
    // Build array of updates from selections
    const updates = Object.entries(selections).map(([id, value]) => ({
      id: parseInt(id, 10),
      new_dsc_prepared: value,
    }));

    if (updates.length === 0) {
      toast.error("Please select Yes or No for at least one DSC.");
      return;
    }

    mutation.mutate(updates);
  };

  const handleDismiss = () => {
    setIsVisible(false);
  };

  // Count how many have been answered
  const answeredCount = Object.keys(selections).length;
  const isSubmitDisabled = mutation.isPending || answeredCount === 0;

  // Show nothing if no data or dismissed
  if (!isVisible || isLoading || expiringDscs.length === 0) return null;

  return (
    <>
      {/* Inject keyframe animation for the spinner */}
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>

      <div style={styles.overlay} onClick={handleDismiss}>
        <div style={styles.card} onClick={(e) => e.stopPropagation()}>
          {/* Header */}
          <div style={styles.header}>
            <div style={styles.iconCircle}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
                <line x1="12" y1="9" x2="12" y2="13" />
                <line x1="12" y1="17" x2="12.01" y2="17" />
              </svg>
            </div>
            <div style={styles.headerText}>
              <h3 style={styles.title}>DSC Expiry Alert</h3>
              <p style={styles.subtitle}>
                {expiringDscs.length} DSC(s) are expiring within 30 days. Please respond for each.
              </p>
            </div>
            <button
              onClick={handleDismiss}
              style={styles.closeBtn}
              onMouseEnter={(e) => (e.currentTarget.style.color = "#fff")}
              onMouseLeave={(e) => (e.currentTarget.style.color = "rgba(255,255,255,0.7)")}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </div>

          {/* Body - Scrollable table */}
          <div style={styles.scrollBody}>
            <div style={styles.infoBar}>
              <strong>⚠️ Action required:</strong> For each director below, indicate whether a new DSC has been prepared. Selecting <strong>"No"</strong> will send weekly email reminders every Monday until the DSC is renewed.
            </div>

            {/* Table */}
            <div style={{ overflowX: "auto" }}>
              <table style={styles.table}>
                <thead>
                  <tr>
                    <th style={styles.th}>#</th>
                    <th style={styles.th}>Director Name</th>
                    <th style={styles.th}>PAN</th>
                    <th style={styles.th}>Expiry Date</th>
                    <th style={styles.th}>Days Left</th>
                  <th style={{ ...styles.th, textAlign: "center" }}>
                    New DSC Prepared?
                  </th>
                  </tr>
                </thead>
                <tbody>
                  {expiringDscs.map((dsc, idx) => {
                    const daysLeft = calcDaysLeft(dsc.to_date);
                    const selected = selections[dsc.id];

                    let badgeStyle = { ...styles.expiryBadge };
                    if (daysLeft !== null) {
                      if (daysLeft <= 0) {
                        badgeStyle = { ...badgeStyle, background: "#fef2f2", color: "#b91c1c" };
                      } else if (daysLeft <= 7) {
                        badgeStyle = { ...badgeStyle, background: "#fffbeb", color: "#d97706" };
                      } else {
                        badgeStyle = { ...badgeStyle, background: "#ecfdf5", color: "#047857" };
                      }
                    }

                    return (
                      <tr
                        key={dsc.id}
                        style={{
                          ...styles.rowHover,
                          background: idx % 2 === 0 ? "#fff" : "#f9fafb",
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.background = "#fefce8";
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.background = idx % 2 === 0 ? "#fff" : "#f9fafb";
                        }}
                      >
                        <td style={styles.td}>{idx + 1}</td>
                        <td style={{ ...styles.td, fontWeight: 500 }}>{dsc.director_name}</td>
                        <td style={styles.td}>
                          <span style={{ fontFamily: "monospace", fontSize: "0.8rem" }}>
                            {dsc.pan || "—"}
                          </span>
                        </td>
                        <td style={styles.td}>
                          <span style={badgeStyle}>
                            <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                              <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
                              <line x1="16" y1="2" x2="16" y2="6" />
                              <line x1="8" y1="2" x2="8" y2="6" />
                              <line x1="3" y1="10" x2="21" y2="10" />
                            </svg>
                            {dsc.to_date || "—"}
                          </span>
                        </td>
                        <td style={styles.td}>
                          {daysLeft !== null ? (
                            <span
                              style={{
                                fontWeight: daysLeft <= 0 ? 700 : daysLeft <= 7 ? 600 : 400,
                                color: daysLeft <= 0 ? "#b91c1c" : daysLeft <= 7 ? "#d97706" : "#374151",
                              }}
                            >
                              {daysLeft <= 0 ? "Expired" : `${daysLeft} day${daysLeft === 1 ? "" : "s"}`}
                            </span>
                          ) : (
                            "—"
                          )}
                        </td>
                        <td style={{ ...styles.td, textAlign: "center" }}>
                          <div style={styles.radioGroup}>
                            {/* Yes radio */}
                            <label
                              style={{
                                ...styles.radioLabel,
                                ...(selected === true ? styles.radioYes : styles.emptyYes),
                                background: selected === true ? "#ecfdf5" : "transparent",
                                border: selected === true ? "1px solid #a7f3d0" : "1px solid transparent",
                              }}
                            >
                              <input
                                type="radio"
                                name={`dsc-${dsc.id}`}
                                checked={selected === true}
                                onChange={() => handleSelection(dsc.id, true)}
                                style={styles.inputRadio}
                              />
                              Yes
                            </label>

                            {/* No radio */}
                            <label
                              style={{
                                ...styles.radioLabel,
                                ...(selected === false ? styles.radioNo : styles.emptyNo),
                                background: selected === false ? "#fef2f2" : "transparent",
                                border: selected === false ? "1px solid #fecaca" : "1px solid transparent",
                              }}
                            >
                              <input
                                type="radio"
                                name={`dsc-${dsc.id}`}
                                checked={selected === false}
                                onChange={() => handleSelection(dsc.id, false)}
                                style={styles.inputRadioRed}
                              />
                              No
                            </label>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* Footer with submit */}
          <div style={styles.footer}>
            <p style={styles.footerInfo}>
              {answeredCount === 0
                ? "Select Yes or No for each DSC above."
                : `${answeredCount} of ${expiringDscs.length} DSC(s) answered.`}
            </p>
            <button
              onClick={handleSubmit}
              disabled={isSubmitDisabled}
              style={{
                ...styles.submitBtn,
                opacity: isSubmitDisabled ? 0.5 : 1,
                cursor: isSubmitDisabled ? "not-allowed" : "pointer",
              }}
              onMouseEnter={(e) => {
                if (!isSubmitDisabled) {
                  e.currentTarget.style.background = "#047857";
                  e.currentTarget.style.transform = "translateY(-1px)";
                  e.currentTarget.style.boxShadow = "0 4px 12px rgba(5,150,105,0.3)";
                }
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = "#059669";
                e.currentTarget.style.transform = "none";
                e.currentTarget.style.boxShadow = "none";
              }}
            >
              {mutation.isPending ? (
                <>
                  <SpinnerIcon size={18} />
                  Submitting...
                </>
              ) : (
                <>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="20 6 9 17 4 12" />
                  </svg>
                  Submit
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </>
  );
}

import { useState, useEffect, useMemo, useCallback } from "react";
import { useQuery } from "@tanstack/react-query";
import { format } from "date-fns";
import { CalendarIcon, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { api } from "iron-stack-ui";
import { FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form.tsx";
import { useWatch, useFormContext } from "react-hook-form";
import { Spinner } from "@/components/ui/spinner.tsx";
import { Input } from "@/components/ui/input.tsx";
import { Textarea } from "@/components/ui/textarea.tsx";
import { Checkbox } from "@/components/ui/checkbox.tsx";
import { Button } from "@/components/ui/button.tsx";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select.tsx";
import { Calendar } from "@/components/ui/calendar.tsx";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover.tsx";
import { cn } from "@/utils/utils.ts";
import { fieldName } from "./formUtils";
import { uploadForm146 } from "../../utils/approval-api";
import { downloadFileWithDialog } from "../../utils/download-utils";

const useTdsRateOptions = () => {
  return useQuery({
    queryKey: ["tds-rate-dropdown"],
    queryFn: async () => {
      const response = await api.get(
        "/masters/TDSRate/dropdown"
      );

      const d = response.data;

      return Array.isArray(d)
        ? d
        : d.results || [];
    },
  });
};

function useDebounce(value, delay) {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(t);
  }, [value, delay]);
  return debounced;
}

function getFkLabel(item, field) {
  if (field?.labelFields?.length) {
    const parts = field.labelFields.map((k) => item[k]).filter((v) => v != null && v !== "");
    if (parts.length) return parts.join(" - ");
  }
  if (item.tds_rate) return String(item.tds_rate);
  if (item.sap_code && item.entity_name) return `${item.sap_code} - ${item.entity_name}`;
  if (item.particular_name) return String(item.particular_name);
  if (item.currency) return String(item.currency);
  return `#${item.id}`;
}

function FkFormField({ control, name, field, disabled, formValues, sectionKey, note, rules, dynamicRequiredFields }) {
  const [search, setSearch] = useState("");
  const debouncedSearch = useDebounce(search, 300);
  const params = useMemo(() => {
    const p = { ...(field.dropdownParams || {}) };
    if (debouncedSearch) {
      p.search = debouncedSearch;
    }
    if (
      field.key === "rbi_sub_code" &&
      formValues?.bank_detail?.rbi_purpose_code
    ) {
      p.rbi_purpose_code =
        formValues.bank_detail.rbi_purpose_code;
    }
    if (
      field.key === "bank_ifsc_code" &&
      formValues?.master?.company
    ) {
      p.legal_entity = formValues.master.company;
    }
    return p;
  }, [field.dropdownParams, debouncedSearch, formValues, field.key]);

  const { data = [] } = useQuery({
    queryKey: [
      "dropdown",
      field.api,
      JSON.stringify(params),
    ],
    queryFn: () =>
      api.get(`/${field.api}/dropdown`, { params }).then((r) => {
        const d = r.data;
        return Array.isArray(d) ? d : d.results || [];
      }),
  });

  const isDisabled = disabled || field.disabled;

  return (
    <FormField
      control={control}
      name={name}
      rules={rules}
      render={({ field: f }) => {
        const selectedItem = (data).find(
          (item) => String(item.id) === String(f.value)
        );
        // Check if we have a display label from backend payload
        const displayLabel = formValues?.[sectionKey]?.[field.key + "_display"];

        return (
          <FormItem>
            <FormLabel>{field.label}{(field.required || dynamicRequiredFields?.has(field.key)) && <span className="text-destructive ml-1">*</span>}</FormLabel>

            {isDisabled && displayLabel ? (
              // Show plain text display when disabled and we have a display label
              <div className="w-full rounded-md border border-input bg-muted/50 px-3 py-2 text-sm text-muted-foreground text-left">
                {displayLabel}
              </div>
            ) : (
              <Select
                disabled={isDisabled}
                value={String(f.value ?? "")}
                onValueChange={(value) => {
                  if (value === "" || value == null) {
                    return;
                  }
                  f.onChange(value);
                }}
              >
                <FormControl>
                  <SelectTrigger className="w-full">
                  <SelectValue
                    placeholder={`Select ${field.label}`}
                  />
                  </SelectTrigger>
                </FormControl>

                <SelectContent>
                  {data.length === 0 ? (
                    <div className="px-3 py-6 text-sm text-muted-foreground text-center">
                      {field.key === "bank_ifsc_code" && formValues?.master?.company
                        ? "No bank accounts found for this company"
                        : `No ${field.label.toLowerCase()} available`}
                    </div>
                  ) : (
                    (data).map((item) => (
                      <SelectItem
                        key={item.id}
                        value={String(item.id)}
                      >
                        {getFkLabel(item, field)}
                      </SelectItem>
                    ))
                  )}
                </SelectContent>
              </Select>
            )}

            <FormMessage />
            {note && (
              <p className="text-xs text-muted-foreground mt-1 italic text-left">{note}</p>
            )}
          </FormItem>
        );
      }}
    />
  );
}

// function SupplierSearchField({ control, name, field, disabled }) {
//   const [search, setSearch] = useState("");

//   const debouncedSearch = useDebounce(search, 300);

//   const params = useMemo(() => {
//     const p = {
//       ...(field.dropdownParams || {}),
//     };

//     if (debouncedSearch) {
//       p.search = debouncedSearch;
//     }

//     return p;
//   }, [field.dropdownParams, debouncedSearch]);

//   const { data = [] } = useQuery({
//     queryKey: [
//       "supplier-dropdown",
//       debouncedSearch,
//     ],

//     queryFn: () =>
//       api.get(`/${field.api}/dropdown`, { params }).then((r) => {
//         const d = r.data;
//         return Array.isArray(d) ? d : d.results || [];
//       }),
//   });

//   return (
//     <FormField
//       control={control}
//       name={name}
//       render={({ field: f }) => (
//         <FormItem>
//           <FormLabel>{field.label}</FormLabel>

//           <Select
//             disabled={disabled || field.disabled}
//             value={f.value || ""}
//             onValueChange={f.onChange}
//           >
//             <FormControl>
//               <SelectTrigger className="w-full">
//                 <SelectValue
//                   placeholder={`Search ${field.label}`}
//                 />
//               </SelectTrigger>
//             </FormControl>

//             <SelectContent>
//               <div className="p-2 pb-1">
//                 <Input
//                   placeholder="Search supplier..."
//                   value={search}
//                   onChange={(e) => setSearch(e.target.value)}
//                   className="h-8 text-sm"
//                   onClick={(e) => e.stopPropagation()}
//                   onKeyDown={(e) => e.stopPropagation()}
//                 />
//               </div>

//               {f.value &&
//               !data.some(
//                 (item) =>
//                   `${item.vendor_name} (${item.vendor_code})` === f.value
//               ) && (
//                 <SelectItem value={f.value}>
//                   {f.value}
//                 </SelectItem>
//               )}

//               {data.map((item) => {
//                 const displayValue =
//                   `${item.vendor_name} (${item.vendor_code})`;

//                 return (
//                   <SelectItem
//                     key={item.id}
//                     value={displayValue}
//                   >
//                     {displayValue}
//                   </SelectItem>
//                 );
//               })}
//             </SelectContent>
//           </Select>

//           <FormMessage />
//         </FormItem>
//       )}
//     />
//   );
// }
function SupplierSearchField({ control, name, field, disabled, rules, dynamicRequiredFields }) {
  const [search, setSearch] = useState("");
  const formValue = useWatch({ control, name });

  // Sync internal search state when form is cleared externally (e.g., Clear button)
  useEffect(() => {
    if (!formValue) {
      setSearch("");
    }
  }, [formValue]);

  const debouncedSearch = useDebounce(search, 300);

  const params = useMemo(() => {
    const p = {
      ...(field.dropdownParams || {}),
    };

    if (debouncedSearch) {
      p.search = debouncedSearch;
    }

    return p;
  }, [field.dropdownParams, debouncedSearch]);

  const { data = [] } = useQuery({
    queryKey: [
      "supplier-dropdown",
      debouncedSearch,
    ],

    queryFn: () =>
      api.get(`/${field.api}/dropdown`, { params }).then((r) => {
        const d = r.data;
        return Array.isArray(d) ? d : d.results || [];
      }),
  });

  return (
    <FormField
      control={control}
      name={name}
      rules={rules}
      render={({ field: f }) => (
        <FormItem>
          <FormLabel>{field.label}{(field.required || dynamicRequiredFields?.has(field.key)) && <span className="text-destructive ml-1">*</span>}</FormLabel>

          <div className="relative">
            <Input
              placeholder="Search Vendor"
              value={search || f.value || ""}
              disabled={disabled || field.disabled}
              onChange={(e) => {
                setSearch(e.target.value);

                if (f.value) {
                  f.onChange("");
                }
              }}
            />

            {search && data.length > 0 && (
              <div className="absolute z-50 mt-1 w-full rounded-md border bg-white shadow-md max-h-60 overflow-auto">
                {data.map((item) => {
                  const displayValue =
                    `${item.vendor_name} (${item.vendor_code})`;

                  return (
                    <div
                      key={item.id}
                      className="cursor-pointer px-3 py-2 text-left hover:bg-gray-100 border-b last:border-b-0"
                      onClick={() => {
                        f.onChange(displayValue);
                        setSearch(displayValue);
                      }}
                    >
                      {displayValue}
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          <FormMessage />
        </FormItem>
      )}
    />
  );
}

export default function StageFormFields({ control, sectionKey, fields, disabled, fileUrls = {}, requestId, values, onRemoveCopiedFile, copiedFileFields = [], onComparisonComplete, approvalMode, approvalToken, dynamicRequiredFields}) {

  const [downloadingUrl, setDownloadingUrl] = useState(null);

  // Get setValue for auto-updating comparison status after upload in approval mode
  const formContext = useFormContext();
  const setValue = formContext?.setValue;

  // Helper: check if a field is required (either statically or dynamically based on particular)
  const isFieldRequired = useCallback((field) => {
    return field.required || dynamicRequiredFields?.has(field.key);
  }, [dynamicRequiredFields]);

  // Helper: generate validation rules for a field based on its type and required flag
  // File fields are excluded from rules to avoid React re-render issues with uncontrolled file inputs.
  // File validation is handled by the backend (_validate_required_fields in engine.py).
  const getFieldRules = (field) => {
    if (!isFieldRequired(field)) return undefined;
    if (field.type === "file") return undefined;
    if (field.type === "checkbox") {
      return { required: `Please check "${field.label}"` };
    }
    return { required: `${field.label} is required` };
  };

  const { data: tdsRateOptions = [] } =
    useTdsRateOptions();

  const handleButtonClick = async (action) => {
    let url;
    let suggestedName;
    switch (action) {
      case "download_form_146":
        url = `/api/tax_requests/tdsopinion/${requestId}/download-form146/`;
        suggestedName = `FORM146_${requestId}.xlsx`;
        break;

      case "download_form_146_comparison":
        url = `/api/tax_requests/tdsopinion/${requestId}/download-form146-comparison/`;
        suggestedName = `FORM146_Comparison_${requestId}.xlsx`;
        break;

      default:
        return;
    }

    try {
      if (action === "download_form_146_comparison") {
        // Get the uploaded file from form state (if any)
        const uploadedFile = values?.[sectionKey]?.form_146_attachment;

        // Build FormData — include file if one was selected
        const formData = new FormData();
        if (uploadedFile instanceof File) {
          formData.append("form_146_attachment", uploadedFile);
        }

        const token = localStorage.getItem("token");
        const response = await fetch(url, {
          method: "POST",
          headers: {
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
            // Do NOT set Content-Type — browser sets it automatically with boundary for FormData
          },
          body: formData,
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => null);
          throw new Error(
            errorData?.detail ||
            `Server returned ${response.status} ${response.statusText}`
          );
        }

        // Parse the JSON response (comparison_status, download URL, etc.)
        const result = await response.json();

        // Download the comparison file if URL is returned
        if (result.download_form_146_comparison) {
          const downloadUrl = result.download_form_146_comparison;
          await downloadFileWithDialog(downloadUrl, { suggestedName });
        }

        // Notify parent to refresh form data (to show updated comparison_status)
        if (onComparisonComplete) {
          onComparisonComplete();
        }
      } else {
        await downloadFileWithDialog(url, { suggestedName });
      }
    } catch (err) {
      if (err.name !== "AbortError") {
        console.error("Download failed:", err);
        toast.error(err.message || "Download failed. Please try again or save the file directly.");
      }
    }
  };
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {fields.map((field) => {
        const name = fieldName(sectionKey, field.key);
        const colSpan = field.type === "textarea" ? "md:col-span-2 lg:col-span-4" : "";

        if (field.type === "tds_rate") {
          return (
            <div key={field.key} className={colSpan}>
              <FormField
                control={control}
                name={name}
                rules={getFieldRules(field)}
                render={({ field: f }) => (
                  <FormItem>
                    <FormLabel>TDS Rate (%){isFieldRequired(field) && <span className="text-destructive ml-1">*</span>}</FormLabel>

                    <Input
                      type="number"
                      list="tds-rate-options"
                      value={f.value ?? ""}
                      onChange={(e) => f.onChange(e.target.value)}
                      placeholder="Enter or Select TDS Rate"
                    />

                    <datalist id="tds-rate-options">
                      {tdsRateOptions.map((item) => (
                        <option
                          key={item.id}
                          value={item.tds_rate}
                        />
                      ))}
                    </datalist>

                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
          );
        }

        if (field.type === "fk") {
          return (
            <div key={field.key} className={colSpan}>
              <FkFormField control={control} name={name} field={field} disabled={disabled || field.disabled} formValues={values} sectionKey={sectionKey} note={field.note} rules={getFieldRules(field)} dynamicRequiredFields={dynamicRequiredFields} />
            </div>
          );
        }

        if (field.type === "supplier_search") {
          return (
            <div key={field.key} className={colSpan}>
              <SupplierSearchField
                control={control}
                name={name}
                field={field}
                disabled={disabled || field.disabled}
                rules={getFieldRules(field)}
                dynamicRequiredFields={dynamicRequiredFields}
              />
            </div>
          );
        }

        if (field.type === "select") {
          return (
            <div key={field.key} className={colSpan}>
              <FormField
                control={control}
                name={name}
                rules={getFieldRules(field)}
                render={({ field: f }) => (
                  <FormItem>
                    <FormLabel>{field.label}{isFieldRequired(field) && <span className="text-destructive ml-1">*</span>}</FormLabel>

                    <Select
                      value={String(f.value ?? "")}
                      onValueChange={f.onChange}
                      disabled={disabled || field.disabled}
                    >
                      <FormControl>
                        <SelectTrigger className="w-full">
                          <SelectValue
                            placeholder={`Select ${field.label}`}
                          />
                        </SelectTrigger>
                      </FormControl>

                      <SelectContent>
                        {field.options.map((option) => (
                          <SelectItem
                            key={option}
                            value={option}
                          >
                            {option}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>

                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
          );
        }

        if (field.type === "checkbox") {
          return (
            <div key={field.key} className={colSpan}>
              <FormField
                control={control}
                name={name}
                rules={getFieldRules(field)}
                render={({ field: f }) => (
                  <FormItem className="flex flex-row items-center gap-3 space-y-0">
                    <FormControl>
                      <Checkbox disabled={disabled || field.disabled} checked={f.value} onCheckedChange={f.onChange} />
                    </FormControl>
                    <FormLabel className="font-normal">{field.label}{isFieldRequired(field) && <span className="text-destructive ml-1">*</span>}</FormLabel>
                  </FormItem>
                )}
              />
            </div>
          );
        }

        if (field.type === "textarea") {
          return (
            <div key={field.key} className={colSpan}>
              <FormField
                control={control}
                name={name}
                rules={getFieldRules(field)}
                render={({ field: f }) => (
                  <FormItem>
                    <FormLabel>{field.label}{isFieldRequired(field) && <span className="text-destructive ml-1">*</span>}</FormLabel>
                    <FormControl>
                      <Textarea disabled={disabled || field.disabled} placeholder={field.label} {...f} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
          );
        }

        if (field.type === "date") {
          // For invoice_posting_date in invoice_posting section, restrict to exchange_rate_date
          const isInvoicePostingDate = sectionKey === "invoice_posting" && field.key === "invoice_posting_date";
          // For proposed_remittance_date in bank_detail section, restrict to dates >= exchange_rate_date
          const isProposedRemittanceDate = sectionKey === "bank_detail" && field.key === "proposed_remittance_date";
          // For ack_date in form_146 section, restrict to dates >= invoice_date
          const isAckDate = sectionKey === "form_146" && field.key === "ack_date";
          // For posting_date in form_145 section, restrict to dates >= invoice_date
          const isForm145PostingDate = sectionKey === "form_145" && field.key === "posting_date";
          // For posting_date in payment_detail section, restrict to dates >= invoice_date
          const isPaymentDetailPostingDate = sectionKey === "payment_detail" && field.key === "posting_date";
          const exchangeRateDate = values?.tds_opinion_stage?.exchange_rate_date;
          const invoiceDate = values?.master?.invoice_date;

          // Disable dates based on field type
          const disabledDays = (exchangeRateDate || invoiceDate)
            ? (date) => {
                const dateStr = format(date, "yyyy-MM-dd");
                if (isInvoicePostingDate && exchangeRateDate) {
                  return dateStr !== exchangeRateDate;
                }
                if (isProposedRemittanceDate && exchangeRateDate) {
                  return dateStr < exchangeRateDate;
                }
                if (isAckDate && invoiceDate) {
                  return dateStr < invoiceDate;
                }
                if (isForm145PostingDate && invoiceDate) {
                  return dateStr < invoiceDate;
                }
                if (isPaymentDetailPostingDate && invoiceDate) {
                  return dateStr < invoiceDate;
                }
                return false;
              }
            : undefined;

          return (
            <div key={field.key} className={colSpan}>
              <FormField
                control={control}
                name={name}
                rules={getFieldRules(field)}
                render={({ field: f }) => (
                  <FormItem className="flex flex-col">
                    <FormLabel>{field.label}{isFieldRequired(field) && <span className="text-destructive ml-1">*</span>}</FormLabel>
                    <Popover>
                      <PopoverTrigger asChild>
                        <FormControl>
                          <Button
                            type="button"
                            variant="outline"
                            disabled={disabled || field.disabled}
                            className={cn("w-full pl-3 text-left font-normal", !f.value && "text-muted-foreground")}
                          >
                            {f.value ? format(new Date(f.value), "yyyy-MM-dd") : "Pick a date"}
                            <CalendarIcon className="ml-auto h-4 w-4 opacity-50" />
                          </Button>
                        </FormControl>
                      </PopoverTrigger>
                      <PopoverContent className="w-auto p-0" align="start">
                        <Calendar
                          mode="single"
                          selected={f.value ? new Date(f.value) : undefined}
                          onSelect={(d) => f.onChange(d ? format(d, "yyyy-MM-dd") : "")}
                          disabled={disabledDays}
                        />
                      </PopoverContent>
                    </Popover>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
          );
        }

        if (field.type === "file") {
          const current = fileUrls[field.key];
          const isCopiedFromExisting = current && onRemoveCopiedFile && copiedFileFields.includes(field.key);
          return (
            <div key={field.key} className={colSpan}>
              <FormField
                control={control}
                name={name}
                rules={getFieldRules(field)}
                render={({ field: f, fieldState }) => {
                  const hasError = !!fieldState.error;

                  return (
                    <FormItem>
                      <FormLabel
                        className={hasError ? "text-destructive" : ""}
                      >
                        {field.label}{isFieldRequired(field) && <span className="text-destructive ml-1">*</span>}
                      </FormLabel>

                      {current && (
                        <div className="mb-1 flex items-center gap-2">
                          <a
                            href={current}
                            onClick={async (e) => {
                              e.preventDefault();
                              if (downloadingUrl) return;
                              setDownloadingUrl(current);
                              try {
                                await downloadFileWithDialog(current);
                              } catch (err) {
                                if (err.name !== "AbortError") {
                                  console.error("Download failed:", err);
                                  toast.error("Download failed. Please try again or save the file directly.");
                                }
                              } finally {
                                setDownloadingUrl((prev) =>
                                  prev === current ? null : prev
                                );
                              }
                            }}
                            className="text-xs text-primary underline cursor-pointer inline-flex items-center gap-1"
                          >
                            {downloadingUrl === current ? (
                              <>
                                <Spinner className="h-3 w-3" />
                                Downloading...
                              </>
                            ) : (
                              "Download current file"
                            )}
                          </a>
                          {isCopiedFromExisting && (
                            <button
                              type="button"
                              onClick={() => onRemoveCopiedFile(field.key)}
                              className="text-destructive hover:text-destructive/80 transition-colors"
                              title="Remove this pre-populated file"
                            >
                              <Trash2 className="h-4 w-4" />
                            </button>
                          )}
                        </div>
                      )}
                      <FormControl>
                        <Input
                          ref={f.ref}
                          name={f.name}
                          type="file"
                          disabled={disabled || field.disabled}
                          aria-invalid={hasError}
                          onBlur={f.onBlur}
                          onChange={async (e) => {
                            const file = e.target.files?.[0] ?? null;

                            // If user uploads a new file for a pre-populated field, remove it from copy list
                            if (file && isCopiedFromExisting) {
                              onRemoveCopiedFile(field.key);
                            }

                            f.onChange(file);

                            // Auto-upload Form 146 PDF in approval mode & run comparison instantly
                            if (file && approvalMode && field.key === "form_146_attachment" && approvalToken) {
                              try {
                                const response = await uploadForm146({ token: approvalToken, file });
                                const result = response.data;

                                // Immediately set comparison status and ack_number from server response
                                if (result.comparison_status && setValue) {
                                  setValue(
                                    fieldName(sectionKey, "comparison_status"),
                                    result.comparison_status
                                  );
                                }
                                if (result.ack_number) {
                                  setValue(
                                    fieldName(sectionKey, "ack_number"),
                                    result.ack_number
                                  );
                                }

                                toast.success("Form 146 uploaded & compared successfully!");

                                // Trigger parent data refetch to sync all fields
                                if (onComparisonComplete) {
                                  onComparisonComplete();
                                }
                              } catch (err) {
                                toast.error(
                                  err?.response?.data?.message ||
                                  err?.response?.data?.detail ||
                                  "Failed to upload Form 146 PDF."
                                );
                              }
                            }
                          }}
                        />
                      </FormControl>

                      <FormMessage />

                      {field.note && (
                        <p className="text-xs text-muted-foreground mt-1 italic text-left">{field.note}</p>
                      )}
                    </FormItem>
                  );
                }}
              />
            </div>
          );
        }

        if (field.type === "button") {
          return (
            <FormItem key={field.key}>
              <FormLabel>{field.label}</FormLabel>

              <Button
                type="button"
                variant="outline"
                onClick={() => handleButtonClick(field.action)}
              >
                Download
              </Button>
            </FormItem>
          );
        }

        if (field.type === "status") {
          return (
            <div key={field.key} className={colSpan}>
              <FormField
                control={control}
                name={name}
                rules={getFieldRules(field)}
                render={({ field: f }) => {
                  const value = f.value;
                  const isPass = value && value.toLowerCase() === "pass";
                  return (
                    <FormItem>
                      <FormLabel>{field.label}</FormLabel>
                      <div
                        className={`w-full text-left text-base font-semibold ${
                          isPass
                            ? "text-green-600"
                            : value
                              ? "text-red-600"
                              : "text-muted-foreground"
                        }`}
                      >
                        {value || "—"}
                      </div>
                    </FormItem>
                  );
                }}
              />
            </div>
          );
        }

        if (field.type === "file_link") {
          const current = fileUrls[field.key];
          return (
            <div key={field.key} className={colSpan}>
              <FormItem>
                <FormLabel>{field.label}</FormLabel>
                <div className="flex items-center gap-2">
                  {current ? (
                    <a
                      href={current}
                      onClick={async (e) => {
                        e.preventDefault();
                        if (downloadingUrl) return;
                        setDownloadingUrl(current);
                        try {
                          await downloadFileWithDialog(current);
                        } catch (err) {
                          if (err.name !== "AbortError") {
                            console.error("Download failed:", err);
                            toast.error("Download failed. Please try again or save the file directly.");
                          }
                        } finally {
                          setDownloadingUrl((prev) =>
                            prev === current ? null : prev
                          );
                        }
                      }}
                      className="text-sm text-primary underline cursor-pointer inline-flex items-center gap-1"
                    >
                      {downloadingUrl === current ? (
                        <>
                          <Spinner className="h-3 w-3" />
                          Downloading...
                        </>
                      ) : (
                        "Download file"
                      )}
                    </a>
                  ) : (
                    <span className="text-sm text-muted-foreground">—</span>
                  )}
                </div>
              </FormItem>
            </div>
          );
        }          return (
            <div key={field.key} className={colSpan}>
              <FormField
                control={control}
                name={name}
                rules={getFieldRules(field)}
                render={({ field: f }) => (
                  <FormItem>
                    <FormLabel>{field.label}{isFieldRequired(field) && <span className="text-destructive ml-1">*</span>}</FormLabel>
                    <FormControl>
                    <Input
                      {...f}
                      type={field.type === "number" ? "number" : "text"}
                      disabled={disabled}
                      readOnly={field.disabled}
                      placeholder={field.label}
                      value={f.value ?? ""}
                      onChange={(e) => {
                        const value =
                          field.type === "number"
                            ? e.target.value === ""
                              ? ""
                              : Number(e.target.value)
                            : e.target.value;

                        f.onChange(value);
                      }}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>
        );
      })}
    </div>
  );
}
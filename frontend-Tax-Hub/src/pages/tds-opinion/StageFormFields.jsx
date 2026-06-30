import { useState, useEffect, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { format } from "date-fns";
import { CalendarIcon, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { api } from "iron-stack-ui";
import { FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form.tsx";
import { useWatch } from "react-hook-form";
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

function getFilenameFromUrl(url) {
  const parts = url.split("/");
  return parts[parts.length - 1] || "download";
}

async function downloadFileWithDialog(url) {
  const filename = getFilenameFromUrl(url);

  // Try the modern File System Access API (shows native Save As dialog)
  if ("showSaveFilePicker" in window) {
    const handle = await window.showSaveFilePicker({
      suggestedName: filename,
    });
    const writable = await handle.createWritable();
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Server returned ${response.status} ${response.statusText}`);
    }
    const blob = await response.blob();
    await writable.write(blob);
    await writable.close();
    return;
  }

  // Fallback: trigger download via anchor element
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}

function FkFormField({ control, name, field, disabled, formValues }) {
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

  return (
    <FormField
      control={control}
      name={name}
      render={({ field: f }) => {
        const selectedItem = (data).find(
          (item) => String(item.id) === String(f.value)
        );
        return (
          <FormItem>
            <FormLabel>{field.label}</FormLabel>

            <Select
              // disabled={disabled}
              disabled={disabled || field.disabled}
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
                {/* <div className="p-2 pb-1">
                  <Input
                    placeholder="Search..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    className="h-8 text-sm"
                    onClick={(e) => e.stopPropagation()}
                    onKeyDown={(e) => e.stopPropagation()}
                  />
                </div> */}

                {(data).map((item) => (
                  <SelectItem
                    key={item.id}
                    value={String(item.id)}
                  >
                    {getFkLabel(item, field)}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <FormMessage />
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
function SupplierSearchField({ control, name, field, disabled }) {
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
      render={({ field: f }) => (
        <FormItem>
          <FormLabel>{field.label}</FormLabel>

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

export default function StageFormFields({ control, sectionKey, fields, disabled, fileUrls = {}, requestId, values, onRemoveCopiedFile, copiedFileFields = []}) {

  const [downloadingUrl, setDownloadingUrl] = useState(null);

  const { data: tdsRateOptions = [] } =
    useTdsRateOptions();

  const handleButtonClick = (action) => {
    switch (action) {
      case "download_form_146":
        window.open(
          `/api/tax_requests/tdsopinion/${requestId}/download-form146/`,
          "_blank"
        );
        break;

      case "download_form_146_comparison":
        window.open(
          `/api/tax_requests/tdsopinion/${requestId}/download-form146-comparison/`,
          "_blank"
        );
        break;

      default:
        break;
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
                render={({ field: f }) => (
                  <FormItem>
                    <FormLabel>TDS Rate (%)</FormLabel>

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
              <FkFormField control={control} name={name} field={field} disabled={disabled || field.disabled} formValues={values} />
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
                render={({ field: f }) => (
                  <FormItem>
                    <FormLabel>{field.label}</FormLabel>

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
                render={({ field: f }) => (
                  <FormItem className="flex flex-row items-center gap-3 space-y-0">
                    <FormControl>
                      <Checkbox disabled={disabled || field.disabled} checked={f.value} onCheckedChange={f.onChange} />
                    </FormControl>
                    <FormLabel className="font-normal">{field.label}</FormLabel>
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
                render={({ field: f }) => (
                  <FormItem>
                    <FormLabel>{field.label}</FormLabel>
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
          return (
            <div key={field.key} className={colSpan}>
              <FormField
                control={control}
                name={name}
                render={({ field: f }) => (
                  <FormItem className="flex flex-col">
                    <FormLabel>{field.label}</FormLabel>
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
                render={({ field: f, fieldState }) => {
                  const hasError = !!fieldState.error;

                  return (
                    <FormItem>
                      <FormLabel
                        className={hasError ? "text-destructive" : ""}
                      >
                        {field.label}
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
                          onChange={(e) => {
                            // If user uploads a new file for a pre-populated field, remove it from copy list
                            if (e.target.files?.[0] && isCopiedFromExisting) {
                              onRemoveCopiedFile(field.key);
                            }
                            f.onChange(e.target.files?.[0] ?? null);
                          }}
                        />
                      </FormControl>

                      <FormMessage />
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

        return (
          <div key={field.key} className={colSpan}>
            <FormField
              control={control}
              name={name}
              render={({ field: f }) => (
                <FormItem>
                  <FormLabel>{field.label}</FormLabel>
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
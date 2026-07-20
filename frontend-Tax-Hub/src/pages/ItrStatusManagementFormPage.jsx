import { useEffect, useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { ArrowLeft, CalendarIcon } from "lucide-react";
import { toast } from "sonner";
import { format } from "date-fns";

import { api } from "iron-stack-ui";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form.tsx";
import { Input } from "@/components/ui/input.tsx";
import { Button } from "@/components/ui/button.tsx";
import { Card } from "@/components/ui/card.tsx";
import { Spinner } from "@/components/ui/spinner.tsx";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select.tsx";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover.tsx";
import { Calendar } from "@/components/ui/calendar.tsx";
import { cn } from "@/utils/utils.ts";

const API_PATH = "registration/itrstatusmanagement";

// Static options for ITR Form dropdown
const itrFormOptions = [
  { id: "ITR 5", label: "ITR 5" },
  { id: "ITR 6", label: "ITR 6" },
  { id: "ITR 7", label: "ITR 7" },
];

// Static options for Filing Type dropdown
const filingTypeOptions = [
  { id: "Original", label: "Original" },
  { id: "Revised", label: "Revised" },
  { id: "Updated", label: "Updated" },
  { id: "Modified", label: "Modified" },
];

// Static options for Status by User dropdown
const statusByUserOptions = [
  { id: "Yet to Start", label: "Yet to Start" },
  { id: "WIP", label: "WIP" },
  { id: "Sent for Review", label: "Sent for Review" },
  { id: "Reviewed", label: "Reviewed" },
  { id: "Uploaded", label: "Uploaded" },
];

export default function ItrStatusManagementFormPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const queryClient = useQueryClient();

  const isEdit = Boolean(id);
  const baseUrl = "itr-status-management";

  // Fetch FK dropdown options
  const financialYearsQuery = useQuery({
    queryKey: ["financial-years", "dropdown"],
    queryFn: () =>
      api.get("/masters/financialyear/dropdown").then((r) => r.data),
  });

  const assessmentYearsQuery = useQuery({
    queryKey: ["assessment-years", "dropdown"],
    queryFn: () =>
      api.get("/masters/assessmentyear/dropdown").then((r) => r.data),
  });

  const legalEntitiesQuery = useQuery({
    queryKey: ["legal-entities", "dropdown"],
    queryFn: () =>
      api.get("/masters/LegalEntity/dropdown").then((r) => r.data),
  });

  const lawSectionsQuery = useQuery({
    queryKey: ["law-sections", "dropdown"],
    queryFn: () =>
      api.get("/masters/LawSection/dropdown").then((r) => r.data),
  });

  // Fetch existing record for edit mode
  const recordQuery = useQuery({
    queryKey: ["itrstatusmanagement", "record", id],
    queryFn: () => api.get(`/${API_PATH}/${id}/`).then((r) => r.data),
    enabled: isEdit,
  });

  const [formReady, setFormReady] = useState(false);

  // Wait for ALL queries AND form reset before rendering form content
  const isLoading = isEdit && (
    recordQuery.isPending ||
    financialYearsQuery.isPending ||
    assessmentYearsQuery.isPending ||
    legalEntitiesQuery.isPending ||
    lawSectionsQuery.isPending ||
    !formReady
  );

  const fv = (field) => recordQuery.data?.[field] ? String(recordQuery.data[field]) : "";
  const form = useForm({
    defaultValues: {
      financial_year: "",
      assessment_year: "",
      pan: "",
      legal_entity: "",
      compliance_section: "",
      filing_type: "",
      itr_form: "",
      acknowledgement_upload: null,
      itr_form_upload: null,
      statutory_timelines: "",
      internal_timelines: "",
      actual_completion_date: "",
      status_by_user: "",
    },
  });

  // Reset formReady when navigating to a new record
  useEffect(() => {
    if (recordQuery.isPending) {
      setFormReady(false);
    }
  }, [recordQuery.isPending]);

  // Populate form with correct FK values, THEN allow form to render
  useEffect(() => {
    if (!recordQuery.data) return;
    form.reset({
      financial_year: fv("financial_year.id"),
      assessment_year: fv("assessment_year.id"),
      pan: fv("pan.id"),
      legal_entity: recordQuery.data.legal_entity || "",
      compliance_section: fv("compliance_section.id"),
      filing_type: recordQuery.data.filing_type || "",
      itr_form: recordQuery.data.itr_form || "",
      acknowledgement_upload: null,
      itr_form_upload: null,
      statutory_timelines: recordQuery.data.statutory_timelines || "",
      internal_timelines: recordQuery.data.internal_timelines || "",
      actual_completion_date: recordQuery.data.actual_completion_date || "",
      status_by_user: recordQuery.data.status_by_user || "",
    });
    setFormReady(true);
  }, [recordQuery.data, form]); // eslint-disable-line react-hooks/exhaustive-deps

  // --- Autofill: when PAN changes, fill legal_entity from selected LegalEntity ---
  const selectedPanId = form.watch("pan");

  useEffect(() => {
    if (!selectedPanId) {
      form.setValue("legal_entity", "");
      return;
    }

    const legalEntities = legalEntitiesQuery.data || [];
    const selected = legalEntities.find(
      (le) => String(le.id) === String(selectedPanId)
    );
    if (selected) {
      form.setValue("legal_entity", selected.entity_name || "");
    }
  }, [selectedPanId, legalEntitiesQuery.data, form]);

  // Navigation helpers
  const pageParam = searchParams.get("page");
  const pageSizeParam = searchParams.get("pageSize");

  const navigateToList = () => {
    const params = new URLSearchParams();
    if (pageParam) params.set("page", pageParam);
    if (pageSizeParam) params.set("pageSize", pageSizeParam);
    const qs = params.toString();
    navigate(`/${baseUrl}${qs ? "?" + qs : ""}`);
  };

  // Submit handler
  const mutation = useMutation({
    mutationFn: (data) => {
      if (isEdit) {
        return api.patch(`/${API_PATH}/${id}/`, data);
      }
      return api.post(`/${API_PATH}/`, data);
    },
    onSuccess: () => {
      toast.success(
        `ITR Status ${isEdit ? "updated" : "created"} successfully`
      );
      queryClient.invalidateQueries({ queryKey: ["itrstatusmanagement"] });
      navigateToList();
    },
    onError: (error) => {
      const detail =
        error.response?.data?.detail ||
        error.response?.data?.non_field_errors?.[0] ||
        JSON.stringify(error.response?.data) ||
        error.message;
      toast.error(`Failed to ${isEdit ? "update" : "create"}: ${detail}`);
    },
  });

  const onSubmit = form.handleSubmit((values) => {
    const hasFile =
      values.acknowledgement_upload instanceof File ||
      values.itr_form_upload instanceof File;

    if (hasFile) {
      const formData = new FormData();
      for (const [key, value] of Object.entries(values)) {
        if (value === "" || value === null || value === undefined) continue;
        if (value instanceof File) {
          formData.append(key, value);
        } else {
          formData.append(key, String(value));
        }
      }
      mutation.mutate(formData);
    } else {
      const payload = {};
      for (const [key, value] of Object.entries(values)) {
        if (value === "" || value === null || value === undefined) continue;
        if (key === "acknowledgement_upload" || key === "itr_form_upload")
          continue;
        payload[key] = value;
      }
      mutation.mutate(payload);
    }
  });

  const title = isEdit ? "Edit ITR Status" : "Create ITR Status";

  const financialYears = financialYearsQuery.data || [];
  const assessmentYears = assessmentYearsQuery.data || [];
  const legalEntities = legalEntitiesQuery.data || [];
  const lawSections = lawSectionsQuery.data || [];

  function renderSelect(fieldName, label, options, displayKey, required) {
    return (
      <FormField
        control={form.control}
        name={fieldName}
        render={({ field }) => (
          <FormItem>
            <FormLabel>
              {label}
              {required && <span className="text-destructive ml-1">*</span>}
            </FormLabel>
            <Select
              onValueChange={field.onChange}
              value={field.value || ""}
            >
              <FormControl>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder={`Select ${label}`} />
                </SelectTrigger>
              </FormControl>
              <SelectContent>
                {options.length === 0 ? (
                  <div className="p-2 text-xs text-muted-foreground">
                    No options found
                  </div>
                ) : (
                  options.map((opt) => (
                    <SelectItem key={opt.id} value={String(opt.id)}>
                      {opt[displayKey] || `#${opt.id}`}
                    </SelectItem>
                  ))
                )}
              </SelectContent>
            </Select>
            <FormMessage />
          </FormItem>
        )}
      />
    );
  }

  function renderTextField(fieldName, label, placeholder) {
    return (
      <FormField
        control={form.control}
        name={fieldName}
        render={({ field }) => (
          <FormItem>
            <FormLabel>{label}</FormLabel>
            <FormControl>
              <Input
                {...field}
                placeholder={placeholder || `Enter ${label}`}
              />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />
    );
  }

  function renderDateField(fieldName, label) {
    return (
      <FormField
        control={form.control}
        name={fieldName}
        render={({ field }) => (
          <FormItem className="flex flex-col">
            <FormLabel>{label}</FormLabel>
            <Popover>
              <PopoverTrigger asChild>
                <FormControl>
                  <Button
                    variant="outline"
                    className={cn(
                      "w-full pl-3 text-left font-normal",
                      !field.value && "text-muted-foreground"
                    )}
                  >
                    {field.value
                      ? format(new Date(field.value), "yyyy-MM-dd")
                      : "Pick a date"}
                    <CalendarIcon className="ml-auto h-4 w-4 opacity-50" />
                  </Button>
                </FormControl>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0" align="start">
                <Calendar
                  mode="single"
                  selected={field.value ? new Date(field.value) : undefined}
                  onSelect={(date) =>
                    field.onChange(date ? format(date, "yyyy-MM-dd") : "")
                  }
                />
              </PopoverContent>
            </Popover>
            <FormMessage />
          </FormItem>
        )}
      />
    );
  }

  return (
    <div className="p-4">
      <div className="flex items-center mb-4">
        <Button
          variant="ghost"
          size="icon"
          onClick={navigateToList}
          className="mr-3"
        >
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <h2 className="text-xl font-bold">{title}</h2>
      </div>

      {isLoading ? (
        <p className="text-sm text-muted-foreground">Loading form…</p>
      ) : (
        <Card size="sm" className="p-5">
          <Form {...form}>
            <form onSubmit={onSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {/* Financial Year — dropdown from FinancialYear Master */}
                {renderSelect(
                  "financial_year",
                  "Financial Year",
                  financialYears,
                  "financial_year"
                )}

                {/* Assessment Year — dropdown from AssessmentYear Master */}
                {renderSelect(
                  "assessment_year",
                  "Assessment Year",
                  assessmentYears,
                  "assessment_year"
                )}

                {/* PAN — dropdown from LegalEntity Master */}
                {renderSelect("pan", "PAN", legalEntities, "pan")}

                {/* Legal Entity — auto-filled from PAN */}
                <FormField
                  control={form.control}
                  name="legal_entity"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Legal Entity</FormLabel>
                      <FormControl>
                        <Input
                          {...field}
                          readOnly
                          placeholder="Auto-filled from PAN"
                          className="bg-muted/30"
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                {/* Compliance Section */}
                {renderSelect(
                  "compliance_section",
                  "Compliance Section",
                  lawSections,
                  "section_2025"
                )}

                {/* Filing Type — dropdown: Original, Revised, Updated, Modified */}
                {renderSelect(
                  "filing_type",
                  "Filing Type",
                  filingTypeOptions,
                  "label"
                )}

                {/* ITR Form — dropdown: ITR 5, ITR 6, ITR 7 */}
                {renderSelect("itr_form", "ITR Form", itrFormOptions, "label")}

                {/* Acknowledgement Upload */}
                <FormField
                  control={form.control}
                  name="acknowledgement_upload"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Acknowledgement Upload</FormLabel>
                      {recordQuery.data?.acknowledgement_upload && !field.value && (
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-xs text-muted-foreground">Current:</span>
                          <a href={recordQuery.data.acknowledgement_upload} target="_blank" rel="noreferrer" className="text-xs font-medium text-primary underline underline-offset-2 hover:text-primary/80">
                            {recordQuery.data.acknowledgement_upload.split("/").pop()}
                          </a>
                        </div>
                      )}
                      <FormControl>
                        <Input
                          type="file"
                          onChange={(e) =>
                            field.onChange(e.target.files?.[0] ?? null)
                          }
                        />
                      </FormControl>
                      {recordQuery.data?.acknowledgement_upload && !field.value && (
                        <p className="text-[11px] text-muted-foreground">Leave empty to keep current file</p>
                      )}
                      <FormMessage />
                    </FormItem>
                  )}
                />

                {/* ITR Form Upload */}
                <FormField
                  control={form.control}
                  name="itr_form_upload"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>ITR Form Upload</FormLabel>
                      {recordQuery.data?.itr_form_upload && !field.value && (
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-xs text-muted-foreground">Current:</span>
                          <a href={recordQuery.data.itr_form_upload} target="_blank" rel="noreferrer" className="text-xs font-medium text-primary underline underline-offset-2 hover:text-primary/80">
                            {recordQuery.data.itr_form_upload.split("/").pop()}
                          </a>
                        </div>
                      )}
                      <FormControl>
                        <Input
                          type="file"
                          onChange={(e) =>
                            field.onChange(e.target.files?.[0] ?? null)
                          }
                        />
                      </FormControl>
                      {recordQuery.data?.itr_form_upload && !field.value && (
                        <p className="text-[11px] text-muted-foreground">Leave empty to keep current file</p>
                      )}
                      <FormMessage />
                    </FormItem>
                  )}
                />

                {/* Statutory Timelines */}
                {renderDateField("statutory_timelines", "Statutory Timelines")}

                {/* Internal Timelines */}
                {renderDateField("internal_timelines", "Internal Timelines")}

                {/* Actual Completion Date */}
                {renderDateField(
                  "actual_completion_date",
                  "Actual Completion Date"
                )}

                {/* Status by User — dropdown: Yet to Start, WIP, Sent for Review, Reviewed, Uploaded */}
                {renderSelect(
                  "status_by_user",
                  "Status by User",
                  statusByUserOptions,
                  "label"
                )}
              </div>

              <div className="flex justify-end gap-2 pt-4">
                <Button
                  type="button"
                  variant="outline"
                  onClick={navigateToList}
                  disabled={mutation.isPending}
                >
                  Cancel
                </Button>
                <Button type="submit" disabled={mutation.isPending}>
                  {mutation.isPending && <Spinner className="mr-2" />}
                  Save
                </Button>
              </div>
            </form>
          </Form>
        </Card>
      )}
    </div>
  );
}

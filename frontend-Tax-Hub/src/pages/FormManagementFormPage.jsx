import { useEffect } from "react";
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
import { Textarea } from "@/components/ui/textarea.tsx";
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
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover.tsx";
import { Calendar } from "@/components/ui/calendar.tsx";
import { cn } from "@/utils/utils.ts";

const API_PATH = "registration/formmanagement";

export default function FormManagementFormPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const queryClient = useQueryClient();

  const isEdit = Boolean(id);
  const baseUrl = "form-management";

  // Fetch all FK dropdown options
  const financialYearsQuery = useQuery({
    queryKey: ["financial-years", "dropdown"],
    queryFn: () => api.get("/masters/financialyear/dropdown").then((r) => r.data),
  });

  const assessmentYearsQuery = useQuery({
    queryKey: ["assessment-years", "dropdown"],
    queryFn: () => api.get("/masters/assessmentyear/dropdown").then((r) => r.data),
  });

  const legalEntitiesQuery = useQuery({
    queryKey: ["legal-entities", "dropdown"],
    queryFn: () => api.get("/masters/LegalEntity/dropdown").then((r) => r.data),
  });

  const compliancesQuery = useQuery({
    queryKey: ["compliances", "dropdown"],
    queryFn: () => api.get("/masters/compliance/dropdown").then((r) => r.data),
  });

  const lawSectionsQuery = useQuery({
    queryKey: ["law-sections", "dropdown"],
    queryFn: () => api.get("/masters/LawSection/dropdown").then((r) => r.data),
  });

  const formMastersQuery = useQuery({
    queryKey: ["form-masters", "dropdown"],
    queryFn: () => api.get("/masters/FormMaster/dropdown").then((r) => r.data),
  });

  // Fetch existing record for edit mode
  const recordQuery = useQuery({
    queryKey: ["formmanagement", "record", id],
    queryFn: () => api.get(`/${API_PATH}/${id}/`).then((r) => r.data),
    enabled: isEdit,
  });

  const form = useForm({
    defaultValues: {
      financial_year: "",
      assessment_year: "",
      pan: "",
      legal_entity: "",
      compliance_name: "",
      compliance_section: "",
      form_no: "",
      form_description: "",
      filing_type: "",
      acknowledgement_upload: null,
      form_upload: null,
      statutory_timelines: "",
      internal_timelines: "",
      actual_completion_date: "",
      status_by_user: "",
    },
  });

  // Populate form when record loads in edit mode
  useEffect(() => {
    if (!recordQuery.data) return;
    form.reset({
      financial_year: recordQuery.data.financial_year ? String(recordQuery.data.financial_year) : "",
      assessment_year: recordQuery.data.assessment_year ? String(recordQuery.data.assessment_year) : "",
      pan: recordQuery.data.pan ? String(recordQuery.data.pan) : "",
      legal_entity: recordQuery.data.legal_entity || "",
      compliance_name: recordQuery.data.compliance_name ? String(recordQuery.data.compliance_name) : "",
      compliance_section: recordQuery.data.compliance_section ? String(recordQuery.data.compliance_section) : "",
      form_no: recordQuery.data.form_no ? String(recordQuery.data.form_no) : "",
      form_description: recordQuery.data.form_description || "",
      filing_type: recordQuery.data.filing_type || "",
      acknowledgement_upload: null,
      form_upload: null,
      statutory_timelines: recordQuery.data.statutory_timelines || "",
      internal_timelines: recordQuery.data.internal_timelines || "",
      actual_completion_date: recordQuery.data.actual_completion_date || "",
      status_by_user: recordQuery.data.status_by_user || "",
    });
  }, [recordQuery.data, form]);

  // --- Autofill: when form_no changes, fill form_description from selected FormMaster ---
  const selectedFormNoId = form.watch("form_no");

  useEffect(() => {
    if (!selectedFormNoId) {
      form.setValue("form_description", "");
      return;
    }

    const formMasters = formMastersQuery.data || [];
    const selected = formMasters.find(
      (fm) => String(fm.id) === String(selectedFormNoId)
    );
    if (selected) {
      form.setValue("form_description", selected.form_description || "");
    }
  }, [selectedFormNoId, formMastersQuery.data, form]);

  // --- Autofill: when pan changes, fill legal_entity from selected LegalEntity ---
  const selectedPanId = form.watch("pan");

  useEffect(() => {
    if (!selectedPanId) {
      form.setValue("legal_entity", "");
      return;
    }
    const entities = legalEntitiesQuery.data || [];
    const selected = entities.find((e) => String(e.id) === String(selectedPanId));
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
      toast.success(`Form Management ${isEdit ? "updated" : "created"} successfully`);
      queryClient.invalidateQueries({ queryKey: ["formmanagement"] });
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
    const hasFile = values.acknowledgement_upload instanceof File || values.form_upload instanceof File;

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
        // Don't send null file when no new file is selected
        if (key === "acknowledgement_upload" || key === "form_upload") continue;
        payload[key] = value;
      }
      mutation.mutate(payload);
    }
  });

  const isLoading = isEdit && recordQuery.isPending;
  const title = isEdit ? "Edit Form Management" : "Create Form Management";

  const financialYears = financialYearsQuery.data || [];
  const assessmentYears = assessmentYearsQuery.data || [];
  const legalEntities = legalEntitiesQuery.data || [];
  const compliances = compliancesQuery.data || [];
  const lawSections = lawSectionsQuery.data || [];
  const formMasters = formMastersQuery.data || [];

  // Static options for filing type dropdown
  const filingTypeOptions = [
    { id: "Original", label: "Original" },
    { id: "Revised", label: "Revised" },
  ];

  // Static options for status by user dropdown
  const statusByUserOptions = [
    { id: "Yet to Start", label: "Yet to Start" },
    { id: "WIP", label: "WIP" },
    { id: "Sent for Review", label: "Sent for Review" },
    { id: "Reviewed", label: "Reviewed" },
    { id: "Uploaded", label: "Uploaded" },
  ];


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
                  <div className="p-2 text-xs text-muted-foreground">No options found</div>
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
              <Input {...field} placeholder={placeholder || `Enter ${label}`} />
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
        <Button variant="ghost" size="icon" onClick={navigateToList} className="mr-3">
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
                {/* Financial Year */}
                {renderSelect("financial_year", "Financial Year", financialYears, "financial_year")}

                {/* Assessment Year */}
                {renderSelect("assessment_year", "Assessment Year", assessmentYears, "assessment_year")}

                {/* PAN — shows PAN number from LegalEntity */}
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

                {/* Compliance Name */}
                {renderSelect("compliance_name", "Compliance Name", compliances, "compliance_name")}

                {/* Compliance Section */}
                {renderSelect("compliance_section", "Compliance Section", lawSections, "section_2025")}

                {/* Form No. */}
                {renderSelect("form_no", "Form No.", formMasters, "form_no")}

                {/* Form No. Description — auto-populated from form_no */}
                <FormField
                  control={form.control}
                  name="form_description"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Form No. Description</FormLabel>
                      <FormControl>
                        <Input
                          {...field}
                          readOnly
                          placeholder="Auto-populated from Form No."
                          className="bg-muted/30"
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                {/* Filing Type — dropdown with Original / Revised */}
                {renderSelect("filing_type", "Filing Type", filingTypeOptions, "label", false)}

                {/* Acknowledgement Upload */}
                <FormField
                  control={form.control}
                  name="acknowledgement_upload"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Acknowledgement Upload</FormLabel>
                      <FormControl>
                        <Input
                          type="file"
                          onChange={(e) => field.onChange(e.target.files?.[0] ?? null)}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                {/* Form Upload */}
                <FormField
                  control={form.control}
                  name="form_upload"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Form Upload</FormLabel>
                      <FormControl>
                        <Input
                          type="file"
                          onChange={(e) => field.onChange(e.target.files?.[0] ?? null)}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                {/* Statutory Timelines */}
                {renderDateField("statutory_timelines", "Statutory Timelines")}

                {/* Internal Timelines */}
                {renderDateField("internal_timelines", "Internal Timelines")}

                {/* Actual Completion Date */}
                {renderDateField("actual_completion_date", "Actual Completion Date")}

                {/* Status by User — dropdown with predefined statuses */}
                {renderSelect("status_by_user", "Status by User", statusByUserOptions, "label", false)}
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

import { useEffect, useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import {
  ArrowLeft,
  CalendarIcon,
  ExternalLink,
  FileText,
  Loader2,
} from "lucide-react";
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

const API_PATH = "registration/compliancemanagement";

// Static options for status by user dropdown
const statusByUserOptions = [
  { id: "Yet to Start", label: "Yet to Start" },
  { id: "WIP", label: "WIP" },
  { id: "Sent for Review", label: "Sent for Review" },
  { id: "Reviewed", label: "Reviewed" },
  { id: "Uploaded", label: "Uploaded" },
];

export default function ComplianceManagementFormPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const queryClient = useQueryClient();

  const isEdit = Boolean(id);
  const baseUrl = "compliance-management";

  // --- State for FormManagement data ---
  const [formManagementDocs, setFormManagementDocs] = useState([]);
  const [isFetchingFormData, setIsFetchingFormData] = useState(false);

  // Fetch all FK dropdown options
  const legalEntitiesQuery = useQuery({
    queryKey: ["legal-entities", "dropdown"],
    queryFn: () =>
      api.get("/masters/LegalEntity/dropdown").then((r) => r.data),
  });

  const verticalsQuery = useQuery({
    queryKey: ["verticals", "dropdown"],
    queryFn: () =>
      api.get("/masters/vertical/dropdown").then((r) => r.data),
  });

  const lawsQuery = useQuery({
    queryKey: ["laws", "dropdown"],
    queryFn: () => api.get("/masters/law/dropdown").then((r) => r.data),
  });

  const compliancesQuery = useQuery({
    queryKey: ["compliances", "dropdown"],
    queryFn: () =>
      api.get("/masters/compliance/dropdown").then((r) => r.data),
  });

  const lawSectionsQuery = useQuery({
    queryKey: ["law-sections", "dropdown"],
    queryFn: () =>
      api.get("/masters/LawSection/dropdown").then((r) => r.data),
  });

  const periodsQuery = useQuery({
    queryKey: ["periods", "dropdown"],
    queryFn: () => api.get("/masters/period/dropdown").then((r) => r.data),
  });

  const userMastersQuery = useQuery({
    queryKey: ["user-masters", "dropdown"],
    queryFn: () =>
      api.get("/masters/usermaster/dropdown").then((r) => r.data),
  });

  // Fetch existing record for edit mode
  const recordQuery = useQuery({
    queryKey: ["compliancemanagement", "record", id],
    queryFn: () => api.get(`/${API_PATH}/${id}/`).then((r) => r.data),
    enabled: isEdit,
  });

  const form = useForm({
    defaultValues: {
      pan: "",
      vertical: "",
      legal_entity: "",
      law_name: "",
      compliance_name: "",
      compliance_section: "",
      period: "",
      frequency: "",
      user_involved: "",
      statutory_timelines: "",
      internal_timelines: "",
      actual_completion_date: "",
      status_by_user: "",
      document_link: null,
      status_by_workspace_admin: "",
      status_from_income_tax_website: "",
    },
  });

  // Populate form when record loads in edit mode
  useEffect(() => {
    if (!recordQuery.data) return;
    form.reset({
      pan: recordQuery.data.pan ? String(recordQuery.data.pan) : "",
      vertical: recordQuery.data.vertical ? String(recordQuery.data.vertical) : "",
      legal_entity: recordQuery.data.legal_entity || "",
      law_name: recordQuery.data.law_name
        ? String(recordQuery.data.law_name)
        : "",
      compliance_name: recordQuery.data.compliance_name
        ? String(recordQuery.data.compliance_name)
        : "",
      compliance_section: recordQuery.data.compliance_section
        ? String(recordQuery.data.compliance_section)
        : "",
      period: recordQuery.data.period ? String(recordQuery.data.period) : "",
      frequency: recordQuery.data.frequency
        ? String(recordQuery.data.frequency)
        : "",
      user_involved: recordQuery.data.user_involved
        ? String(recordQuery.data.user_involved)
        : "",
      statutory_timelines: recordQuery.data.statutory_timelines || "",
      internal_timelines: recordQuery.data.internal_timelines || "",
      actual_completion_date: recordQuery.data.actual_completion_date || "",
      status_by_user: recordQuery.data.status_by_user || "",
      document_link: null,
      status_by_workspace_admin:
        recordQuery.data.status_by_workspace_admin || "",
      status_from_income_tax_website:
        recordQuery.data.status_from_income_tax_website || "",
    });

    // Also load FormManagement documents if PAN is set in edit mode
    const panId = recordQuery.data.pan;
    if (panId) {
      fetchFormManagementData(panId);
    }
  }, [recordQuery.data, form]);

  // --- Autofill: when PAN changes, fill legal_entity & fetch FormManagement data ---
  const selectedPanId = form.watch("pan");

  useEffect(() => {
    if (!selectedPanId) {
      form.setValue("legal_entity", "");
      setFormManagementDocs([]);
      return;
    }

    // Auto-fill legal entity name from LegalEntity dropdown data
    const legalEntities = legalEntitiesQuery.data || [];
    const selected = legalEntities.find(
      (le) => String(le.id) === String(selectedPanId)
    );
    if (selected) {
      form.setValue("legal_entity", selected.entity_name || "");
    }

    // Fetch FormManagement data for auto-population
    fetchFormManagementData(selectedPanId);
  }, [selectedPanId, legalEntitiesQuery.data, form]);

  // --- Autofill: frequency from compliance_name ---
  const selectedComplianceNameId = form.watch("compliance_name");

  useEffect(() => {
    if (!selectedComplianceNameId) return;
    const currentFrequency = form.getValues("frequency");
    if (currentFrequency) return; // don't override if already set

    const compliances = compliancesQuery.data || [];
    const selected = compliances.find(
      (c) => String(c.id) === String(selectedComplianceNameId)
    );
    if (selected) {
      form.setValue("frequency", String(selected.id));
    }
  }, [selectedComplianceNameId, compliancesQuery.data, form]);

  // --- Fetch FormManagement data by PAN ---
  async function fetchFormManagementData(panId) {
    if (!panId) return;
    setIsFetchingFormData(true);
    try {
      const response = await api.get(
        `/registration/formmanagement-by-pan/${panId}/`
      );
      const data = response.data;

      // Auto-populate fields from latest FormManagement record
      if (data.latest) {
        // Only set if the field is currently empty
        const fields = [
          "statutory_timelines",
          "internal_timelines",
          "actual_completion_date",
          "status_by_user",
        ];
        fields.forEach((field) => {
          const currentValue = form.getValues(field);
          if (!currentValue && data.latest[field]) {
            form.setValue(field, data.latest[field]);
          }
        });
      }

      // Store documents for display
      if (data.documents) {
        setFormManagementDocs(data.documents);
      }
    } catch (error) {
      // Silently fail — auto-population is a convenience, not critical
      console.error("Failed to fetch FormManagement data:", error);
    } finally {
      setIsFetchingFormData(false);
    }
  }

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
        `Compliance Management ${isEdit ? "updated" : "created"} successfully`
      );
      queryClient.invalidateQueries({
        queryKey: ["compliancemanagement"],
      });
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
    const hasFile = values.document_link instanceof File;

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
        if (key === "document_link") continue;
        payload[key] = value;
      }
      mutation.mutate(payload);
    }
  });

  const isLoading = isEdit && recordQuery.isPending;
  const title = isEdit
    ? "Edit Compliance Management"
    : "Create Compliance Management";

  const legalEntities = legalEntitiesQuery.data || [];
  const verticals = verticalsQuery.data || [];
  const laws = lawsQuery.data || [];
  const compliances = compliancesQuery.data || [];
  const lawSections = lawSectionsQuery.data || [];
  const periods = periodsQuery.data || [];
  const userMasters = userMastersQuery.data || [];

  // Helper: get document URL
  function getDocumentUrl(filePath) {
    if (!filePath) return null;
    const baseUrl =
      import.meta.env.VITE_API_BASE_URL?.replace("/api", "") ||
      "http://127.0.0.1:8000";
    if (filePath.startsWith("http")) return filePath;
    return `${baseUrl}${filePath.startsWith("/") ? "" : "/"}${filePath}`;
  }

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
                {/* PAN — dropdown from LegalEntity Master */}
                {renderSelect("pan", "PAN", legalEntities, "pan")}

                {/* Vertical — dropdown from Vertical Master */}
                {renderSelect("vertical", "Vertical", verticals, "particulars")}

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

                {/* Law Name */}
                {renderSelect("law_name", "Law Name", laws, "law_name")}

                {/* Compliance Name */}
                {renderSelect(
                  "compliance_name",
                  "Compliance Name",
                  compliances,
                  "compliance_name"
                )}

                {/* Compliance Section */}
                {renderSelect(
                  "compliance_section",
                  "Compliance Section",
                  lawSections,
                  "section_2025"
                )}

                {/* Period */}
                {renderSelect("period", "Period", periods, "category")}

                {/* Frequency — auto-filled from Compliance Name */}
                {renderSelect(
                  "frequency",
                  "Frequency",
                  compliances,
                  "frequency"
                )}

                {/* User Involved */}
                {renderSelect(
                  "user_involved",
                  "User Involved",
                  userMasters,
                  "employee_name"
                )}

                {/* Statutory Timelines — auto-populated from FormManagement */}
                {renderDateField(
                  "statutory_timelines",
                  "Statutory Timelines"
                )}

                {/* Internal Timelines — auto-populated from FormManagement */}
                {renderDateField("internal_timelines", "Internal Timelines")}

                {/* Actual Completion Date — auto-populated from FormManagement */}
                {renderDateField(
                  "actual_completion_date",
                  "Actual Completion Date"
                )}

                {/* Status by User — auto-populated from FormManagement */}
                {renderSelect(
                  "status_by_user",
                  "Status by User",
                  statusByUserOptions,
                  "label"
                )}

                {/* Document Link */}
                <FormField
                  control={form.control}
                  name="document_link"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Document Link</FormLabel>
                      <FormControl>
                        <Input
                          type="file"
                          onChange={(e) =>
                            field.onChange(e.target.files?.[0] ?? null)
                          }
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                {/* Status by Workspace Admin */}
                {renderTextField(
                  "status_by_workspace_admin",
                  "Status by Workspace Admin",
                  "Enter status"
                )}

                {/* Status from Income Tax Website */}
                {renderTextField(
                  "status_from_income_tax_website",
                  "Status from Income Tax Website",
                  "Enter status"
                )}
              </div>

              {/* Form Management Documents Section — shows when PAN is selected */}
              {selectedPanId && (
                <Card className="mt-6 p-4 bg-muted/20">
                  <div className="flex items-center gap-2 mb-3">
                    <FileText className="h-4 w-4 text-primary" />
                    <h3 className="text-sm font-semibold">
                      Documents from Form Management
                    </h3>
                    {isFetchingFormData && (
                      <Loader2 className="h-3.5 w-3.5 animate-spin text-muted-foreground" />
                    )}
                  </div>

                  {formManagementDocs.length === 0 && !isFetchingFormData ? (
                    <p className="text-xs text-muted-foreground">
                      No Form Management records found for this PAN.
                    </p>
                  ) : (
                    <div className="space-y-2">
                      {formManagementDocs.map((doc, idx) => (
                        <div
                          key={doc.id || idx}
                          className="flex flex-wrap items-center gap-3 text-xs border rounded-md p-2 bg-background"
                        >
                          <span className="font-medium text-primary min-w-[60px]">
                            {doc.form_no__form_no || `#${doc.id}`}
                          </span>
                          {doc.form_description && (
                            <span className="text-muted-foreground truncate max-w-[180px]">
                              {doc.form_description}
                            </span>
                          )}
                          <div className="flex items-center gap-2 ml-auto">
                            {doc.acknowledgement_upload && (
                              <a
                                href={getDocumentUrl(
                                  doc.acknowledgement_upload
                                )}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="inline-flex items-center gap-1 text-blue-600 hover:text-blue-800 underline"
                              >
                                <ExternalLink className="h-3 w-3" />
                                Acknowledgement
                              </a>
                            )}
                            {doc.form_upload && (
                              <a
                                href={getDocumentUrl(doc.form_upload)}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="inline-flex items-center gap-1 text-blue-600 hover:text-blue-800 underline"
                              >
                                <ExternalLink className="h-3 w-3" />
                                Form Upload
                              </a>
                            )}
                            {!doc.acknowledgement_upload &&
                              !doc.form_upload && (
                                <span className="text-muted-foreground">
                                  No documents
                                </span>
                              )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </Card>
              )}

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

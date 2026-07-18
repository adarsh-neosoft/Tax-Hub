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

const API_PATH = "registration/tasktracker";

// Static options for priority
const priorityOptions = [
  { id: "Low", label: "Low" },
  { id: "Medium", label: "Medium" },
  { id: "High", label: "High" },
];

// Static options for status
const statusOptions = [
  { id: "Open", label: "Open" },
  { id: "WIP", label: "WIP" },
  { id: "Close", label: "Close" },
];

export default function TaskTrackerFormPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const queryClient = useQueryClient();

  const isEdit = Boolean(id);
  const baseUrl = "task-tracker";

  // Fetch all FK dropdown options
  const periodsQuery = useQuery({
    queryKey: ["periods", "dropdown"],
    queryFn: () => api.get("/masters/period/dropdown").then((r) => r.data),
  });

  const legalEntitiesQuery = useQuery({
    queryKey: ["legal-entities", "dropdown"],
    queryFn: () =>
      api.get("/masters/LegalEntity/dropdown").then((r) => r.data),
  });

  const userMastersQuery = useQuery({
    queryKey: ["user-masters", "dropdown"],
    queryFn: () =>
      api.get("/masters/usermaster/dropdown").then((r) => r.data),
  });

  // Fetch existing record for edit mode
  const recordQuery = useQuery({
    queryKey: ["tasktracker", "record", id],
    queryFn: () => api.get(`/${API_PATH}/${id}/`).then((r) => r.data),
    enabled: isEdit,
  });

  const form = useForm({
    defaultValues: {
      fy: "",
      legal_entity_code: "",
      legal_entity: "",
      task_name: "",
      assign_to: "",
      priority: "",
      status: "",
      statutory_date: "",
      internal_date: "",
      reminder_date: "",
    },
  });

  // Populate form when record loads in edit mode
  useEffect(() => {
    if (!recordQuery.data) return;
    form.reset({
      fy: recordQuery.data.fy ? String(recordQuery.data.fy) : "",
      legal_entity_code: recordQuery.data.legal_entity_code || "",
      legal_entity: recordQuery.data.legal_entity
        ? String(recordQuery.data.legal_entity)
        : "",
      task_name: recordQuery.data.task_name || "",
      assign_to: recordQuery.data.assign_to
        ? String(recordQuery.data.assign_to)
        : "",
      priority: recordQuery.data.priority || "",
      status: recordQuery.data.status || "",
      statutory_date: recordQuery.data.statutory_date || "",
      internal_date: recordQuery.data.internal_date || "",
      reminder_date: recordQuery.data.reminder_date || "",
    });
  }, [recordQuery.data, form]);

  // --- Autofill: when legal_entity (Legal Entity Name) changes, fill legal_entity_code ---
  const selectedLegalEntityId = form.watch("legal_entity");

  useEffect(() => {
    if (!selectedLegalEntityId) {
      form.setValue("legal_entity_code", "");
      return;
    }

    const entities = legalEntitiesQuery.data || [];
    const selected = entities.find(
      (e) => String(e.id) === String(selectedLegalEntityId)
    );
    if (selected) {
      form.setValue("legal_entity_code", selected.sap_code || "");
    }
  }, [selectedLegalEntityId, legalEntitiesQuery.data, form]);

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
        `Task Tracker ${isEdit ? "updated" : "created"} successfully`
      );
      queryClient.invalidateQueries({ queryKey: ["tasktracker"] });
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
    const payload = {};
    for (const [key, value] of Object.entries(values)) {
      if (value === "" || value === null || value === undefined) continue;
      payload[key] = value;
    }
    mutation.mutate(payload);
  });

  const isLoading = isEdit && recordQuery.isPending;
  const title = isEdit ? "Edit Task Tracker" : "Create Task Tracker";

  const periods = periodsQuery.data || [];
  const legalEntities = legalEntitiesQuery.data || [];
  const userMasters = userMastersQuery.data || [];

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
                {/* FY — Dropdown from Period Master */}
                {renderSelect("fy", "FY", periods, "category")}

                {/* Legal Entity Code — auto-filled from Legal Entity Name */}
                <FormField
                  control={form.control}
                  name="legal_entity_code"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Legal Entity Code</FormLabel>
                      <FormControl>
                        <Input
                          {...field}
                          readOnly
                          placeholder="Auto-filled from Legal Entity Name"
                          className="bg-muted/30"
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                {/* Legal Entity Name — Dropdown from Legal Entity Master */}
                {renderSelect(
                  "legal_entity",
                  "Legal Entity Name",
                  legalEntities,
                  "entity_name"
                )}

                {/* Task Name */}
                {renderTextField("task_name", "Task Name", "Enter task name")}

                {/* Assign To — Dropdown from User Master */}
                {renderSelect(
                  "assign_to",
                  "Assign To",
                  userMasters,
                  "employee_name"
                )}

                {/* Priority — Low / Medium / High */}
                {renderSelect(
                  "priority",
                  "Priority",
                  priorityOptions,
                  "label"
                )}

                {/* Status — Open / WIP / Close */}
                {renderSelect("status", "Status", statusOptions, "label")}

                {/* Statutory Date */}
                {renderDateField("statutory_date", "Statutory Date")}

                {/* Internal Date */}
                {renderDateField("internal_date", "Internal Date")}

                {/* Reminder Date */}
                {renderDateField("reminder_date", "Reminder Date")}
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

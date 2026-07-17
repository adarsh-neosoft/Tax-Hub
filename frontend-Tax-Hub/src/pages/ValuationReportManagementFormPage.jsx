import { useEffect, useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import {
  ArrowLeft,
  CalendarIcon,
  Check,
  ChevronDown,
  Search,
  X,
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
import { Checkbox } from "@/components/ui/checkbox.tsx";
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

const API_PATH = "registration/valuationreportmanagement";

export default function ValuationReportManagementFormPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const queryClient = useQueryClient();

  const isEdit = Boolean(id);
  const baseUrl = "valuation-report-management";

  // State for multi-select dropdown
  const [teamMembersOpen, setTeamMembersOpen] = useState(false);
  const [teamMembersSearch, setTeamMembersSearch] = useState("");

  // Fetch dropdown options
  const legalEntitiesQuery = useQuery({
    queryKey: ["legal-entities", "dropdown"],
    queryFn: () =>
      api.get("/masters/LegalEntity/dropdown").then((r) => r.data),
  });

  const lawsQuery = useQuery({
    queryKey: ["laws", "dropdown"],
    queryFn: () => api.get("/masters/law/dropdown").then((r) => r.data),
  });

  const userMastersQuery = useQuery({
    queryKey: ["user-masters", "dropdown"],
    queryFn: () =>
      api.get("/masters/usermaster/dropdown").then((r) => r.data),
  });

  // Fetch existing record for edit mode
  const recordQuery = useQuery({
    queryKey: ["valuationreportmanagement", "record", id],
    queryFn: () => api.get(`/${API_PATH}/${id}/`).then((r) => r.data),
    enabled: isEdit,
  });

  const form = useForm({
    defaultValues: {
      name_of_firm_counsel: "",
      entity: "",
      purpose: "",
      date_of_report: "",
      attachment: null,
      team_members_involved: [],
    },
  });

  // Populate form when record loads in edit mode
  useEffect(() => {
    if (!recordQuery.data) return;
    const m2mValue = recordQuery.data.team_members_involved || [];
    form.reset({
      name_of_firm_counsel: recordQuery.data.name_of_firm_counsel || "",
      entity: recordQuery.data.entity ? String(recordQuery.data.entity) : "",
      purpose: recordQuery.data.purpose ? String(recordQuery.data.purpose) : "",
      date_of_report: recordQuery.data.date_of_report || "",
      attachment: null,
      team_members_involved: Array.isArray(m2mValue)
        ? m2mValue.map(String)
        : [],
    });
  }, [recordQuery.data, form]);

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
        `Valuation Report ${isEdit ? "updated" : "created"} successfully`
      );
      queryClient.invalidateQueries({
        queryKey: ["valuationreportmanagement"],
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
    const hasFile = values.attachment instanceof File;
    const payload = {};
    for (const [key, value] of Object.entries(values)) {
      if (value === "" || value === null || value === undefined) continue;
      if (key === "attachment") {
        if (value instanceof File) payload[key] = value;
        continue;
      }
      payload[key] = value;
    }
    if (
      values.team_members_involved &&
      Array.isArray(values.team_members_involved)
    ) {
      payload.team_members_involved = values.team_members_involved.map(Number);
    }
    if (hasFile) {
      const formData = new FormData();
      for (const [key, value] of Object.entries(payload)) {
        if (value instanceof File) {
          formData.append(key, value);
        } else if (Array.isArray(value)) {
          value.forEach((v) => formData.append(key, String(v)));
        } else {
          formData.append(key, String(value));
        }
      }
      mutation.mutate(formData);
    } else {
      mutation.mutate(payload);
    }
  });

  const isLoading = isEdit && recordQuery.isPending;
  const title = isEdit
    ? "Edit Valuation Report"
    : "Create Valuation Report";

  const legalEntities = legalEntitiesQuery.data || [];
  const laws = lawsQuery.data || [];
  const userMasters = userMastersQuery.data || [];

  // Multi-select helpers
  const selectedTeamMembers = form.watch("team_members_involved") || [];
  const filteredUsers = teamMembersSearch
    ? userMasters.filter((u) =>
        (u.employee_name || "")
          .toLowerCase()
          .includes(teamMembersSearch.toLowerCase())
      )
    : userMasters;

  const toggleTeamMember = (userId) => {
    const current = [...selectedTeamMembers];
    const strId = String(userId);
    if (current.includes(strId)) {
      form.setValue(
        "team_members_involved",
        current.filter((id) => id !== strId)
      );
    } else {
      form.setValue("team_members_involved", [...current, strId]);
    }
  };

  const getUserLabel = (userId) => {
    const user = userMasters.find((u) => String(u.id) === String(userId));
    return user?.employee_name || `#${userId}`;
  };

  const removeTeamMember = (userId, e) => {
    e.stopPropagation();
    toggleTeamMember(userId);
  };

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
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Name of Firm/Counsel */}
                {renderTextField(
                  "name_of_firm_counsel",
                  "Name of the Firm/ Counsel",
                  "Enter firm or counsel name"
                )}

                {/* Entity — dropdown from LegalEntity Master */}
                {renderSelect(
                  "entity",
                  "Name of Entity",
                  legalEntities,
                  "entity_name"
                )}

                {/* Purpose — dropdown from Law Master */}
                {renderSelect("purpose", "Purpose", laws, "law_name")}

                {/* Date of Report */}
                {renderDateField("date_of_report", "Date of Report")}

                {/* Attachment */}
                <FormField
                  control={form.control}
                  name="attachment"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Attachment (Download)</FormLabel>
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

                {/* Team Members Involved — multi-select dropdown */}
                <FormField
                  control={form.control}
                  name="team_members_involved"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Team Members Involved</FormLabel>
                      <Popover
                        open={teamMembersOpen}
                        onOpenChange={setTeamMembersOpen}
                      >
                        <PopoverTrigger asChild>
                          <FormControl>
                            <Button
                              variant="outline"
                              role="combobox"
                              className={cn(
                                "w-full h-auto min-h-10 justify-between font-normal",
                                !selectedTeamMembers.length &&
                                  "text-muted-foreground"
                              )}
                            >
                              <div className="flex flex-wrap gap-1.5 items-center flex-1">
                                {selectedTeamMembers.length === 0 ? (
                                  <span className="text-sm">
                                    Select team members...
                                  </span>
                                ) : (
                                  <div className="flex flex-wrap gap-1">
                                    {selectedTeamMembers
                                      .slice(0, 3)
                                      .map((id) => (
                                        <span
                                          key={id}
                                          className="inline-flex items-center gap-1 text-xs bg-primary/10 text-primary rounded-md px-2 py-0.5"
                                        >
                                          {getUserLabel(id)}
                                          <button
                                            type="button"
                                            onClick={(e) =>
                                              removeTeamMember(id, e)
                                            }
                                            className="hover:text-destructive transition-colors"
                                          >
                                            <X className="h-3 w-3" />
                                          </button>
                                        </span>
                                      ))}
                                    {selectedTeamMembers.length > 3 && (
                                      <span className="text-xs text-muted-foreground">
                                        +{selectedTeamMembers.length - 3} more
                                      </span>
                                    )}
                                  </div>
                                )}
                              </div>
                              <ChevronDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                            </Button>
                          </FormControl>
                        </PopoverTrigger>
                        <PopoverContent
                          className="w-[320px] p-0"
                          align="start"
                        >
                          <div className="flex items-center border-b px-3">
                            <Search className="mr-2 h-4 w-4 shrink-0 opacity-50" />
                            <input
                              placeholder="Search team members..."
                              className="flex h-10 w-full bg-transparent text-sm outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50"
                              value={teamMembersSearch}
                              onChange={(e) =>
                                setTeamMembersSearch(e.target.value)
                              }
                              autoFocus
                            />
                          </div>
                          <div className="max-h-60 overflow-y-auto p-1">
                            {filteredUsers.length === 0 ? (
                              <div className="p-2 text-xs text-muted-foreground text-center">
                                No users found
                              </div>
                            ) : (
                              filteredUsers.map((user) => {
                                const isSelected =
                                  selectedTeamMembers.includes(
                                    String(user.id)
                                  );
                                return (
                                  <div
                                    key={user.id}
                                    className={cn(
                                      "flex items-center gap-2 px-2 py-1.5 rounded-sm cursor-pointer text-sm transition-colors",
                                      isSelected
                                        ? "bg-primary/10 text-primary"
                                        : "hover:bg-muted"
                                    )}
                                    onClick={() => toggleTeamMember(user.id)}
                                  >
                                    <Checkbox
                                      checked={isSelected}
                                      className="data-[state=checked]:bg-primary data-[state=checked]:text-primary-foreground"
                                    />
                                    <span className="flex-1 truncate">
                                      {user.employee_name || `#${user.id}`}
                                    </span>
                                    {isSelected && (
                                      <Check className="h-4 w-4 shrink-0 text-primary" />
                                    )}
                                  </div>
                                );
                              })
                            )}
                          </div>
                        </PopoverContent>
                      </Popover>
                      <FormMessage />
                    </FormItem>
                  )}
                />
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

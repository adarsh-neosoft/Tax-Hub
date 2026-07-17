import { useEffect, useRef, useState } from "react";
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
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover.tsx";
import { Calendar } from "@/components/ui/calendar.tsx";
import { cn } from "@/utils/utils.ts";

const API_PATH = "registration/poatracker";
const BASE_URL = import.meta.env.VITE_API_BASE_URL || "";

export default function PoaTrackerFormPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const queryClient = useQueryClient();

  const isEdit = Boolean(id);
  const baseUrl = "poa-tracker";
  const fileRef = useRef(null);

  // Fetch FK dropdown options
  const legalEntitiesQuery = useQuery({
    queryKey: ["legal-entities", "dropdown"],
    queryFn: () => api.get("/masters/LegalEntity/dropdown").then((r) => r.data),
  });

  const forumsQuery = useQuery({
    queryKey: ["forums", "dropdown"],
    queryFn: () => api.get("/masters/forum/dropdown").then((r) => r.data),
  });

  // Fetch existing record for edit mode
  const recordQuery = useQuery({
    queryKey: ["poatracker", "record", id],
    queryFn: () => api.get(`/${API_PATH}/${id}/`).then((r) => r.data),
    enabled: isEdit,
  });

  const legalEntities = legalEntitiesQuery.data || [];
  const forums = forumsQuery.data || [];

  const form = useForm({
    defaultValues: {
      entity_name: "",
      poa_holder_name: "",
      forum: "",
      pan: "",
      from_date: "",
      to_date: "",
      poa_repository: null,
    },
  });

  const [currentFileUrl, setCurrentFileUrl] = useState("");

  // Populate form when record loads in edit mode
  useEffect(() => {
    if (!recordQuery.data) return;
    form.reset({
      entity_name: recordQuery.data.entity_name || "",
      poa_holder_name: recordQuery.data.poa_holder_name || "",
      forum: recordQuery.data.forum ? String(recordQuery.data.forum) : "",
      pan: recordQuery.data.pan || "",
      from_date: recordQuery.data.from_date || "",
      to_date: recordQuery.data.to_date || "",
      poa_repository: null, // Can't pre-fill file input
    });
    if (recordQuery.data.poa_repository) {
      setCurrentFileUrl(recordQuery.data.poa_repository);
    }
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
      const config = data instanceof FormData
        ? { headers: { "Content-Type": "multipart/form-data" } }
        : {};
      if (isEdit) {
        return api.patch(`/${API_PATH}/${id}/`, data, config);
      }
      return api.post(`/${API_PATH}/`, data, config);
    },
    onSuccess: () => {
      toast.success(`POA Tracker ${isEdit ? "updated" : "created"} successfully`);
      queryClient.invalidateQueries({ queryKey: ["poatracker"] });
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
    const hasFile = values.poa_repository instanceof File;

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
        if (key === "poa_repository") continue;
        payload[key] = value;
      }
      mutation.mutate(payload);
    }
  });

  const isLoading = isEdit && recordQuery.isPending;
  const title = isEdit ? "Edit POA Tracker" : "Create POA Tracker";

  // Build URL for current file
  const mediaUrl = currentFileUrl
    ? currentFileUrl.startsWith("http")
      ? currentFileUrl
      : `${BASE_URL.replace("/api", "")}${currentFileUrl.startsWith("/") ? "" : "/media/"}${currentFileUrl}`
    : "";

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
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Name of Entity — dropdown from LegalEntity Master */}
                <FormField
                  control={form.control}
                  name="entity_name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Name of Entity</FormLabel>
                      <Select
                        onValueChange={field.onChange}
                        value={field.value || ""}
                      >
                        <FormControl>
                          <SelectTrigger className="w-full">
                            <SelectValue placeholder="Select Entity" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          {legalEntities.length === 0 ? (
                            <div className="p-2 text-xs text-muted-foreground">
                              No entities found
                            </div>
                          ) : (
                            legalEntities.map((le) => (
                              <SelectItem key={le.id} value={String(le.id)}>
                                {le.entity_name || `#${le.id}`}
                              </SelectItem>
                            ))
                          )}
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                {/* Name of POA Holder */}
                <FormField
                  control={form.control}
                  name="poa_holder_name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Name of POA Holder</FormLabel>
                      <FormControl>
                        <Input {...field} placeholder="Enter POA holder name" />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                {/* Forum — dropdown WITHOUT search bar */}
                <FormField
                  control={form.control}
                  name="forum"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Forum</FormLabel>
                      <Select
                        onValueChange={field.onChange}
                        value={field.value || ""}
                      >
                        <FormControl>
                          <SelectTrigger className="w-full">
                            <SelectValue placeholder="Select Forum" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          {forums.map((f) => (
                            <SelectItem key={f.id} value={String(f.id)}>
                              {f.forum_name}
                            </SelectItem>
                          ))}
                          {!forums.length && (
                            <div className="p-2 text-xs text-muted-foreground">
                              No forums found
                            </div>
                          )}
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                {/* PAN */}
                <FormField
                  control={form.control}
                  name="pan"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>PAN</FormLabel>
                      <FormControl>
                        <Input {...field} placeholder="Enter PAN" />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                {/* From Date */}
                <FormField
                  control={form.control}
                  name="from_date"
                  render={({ field }) => (
                    <FormItem className="flex flex-col">
                      <FormLabel>From Date</FormLabel>
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
                                ? format(field.value, "yyyy-MM-dd")
                                : "Pick a date"}
                              <CalendarIcon className="ml-auto h-4 w-4 opacity-50" />
                            </Button>
                          </FormControl>
                        </PopoverTrigger>
                        <PopoverContent className="w-auto p-0" align="start">
                          <Calendar
                            mode="single"
                            selected={
                              field.value ? new Date(field.value) : undefined
                            }
                            onSelect={(date) =>
                              field.onChange(
                                date ? format(date, "yyyy-MM-dd") : ""
                              )
                            }
                          />
                        </PopoverContent>
                      </Popover>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                {/* To Date */}
                <FormField
                  control={form.control}
                  name="to_date"
                  render={({ field }) => (
                    <FormItem className="flex flex-col">
                      <FormLabel>To Date</FormLabel>
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
                                ? format(field.value, "yyyy-MM-dd")
                                : "Pick a date"}
                              <CalendarIcon className="ml-auto h-4 w-4 opacity-50" />
                            </Button>
                          </FormControl>
                        </PopoverTrigger>
                        <PopoverContent className="w-auto p-0" align="start">
                          <Calendar
                            mode="single"
                            selected={
                              field.value ? new Date(field.value) : undefined
                            }
                            onSelect={(date) =>
                              field.onChange(
                                date ? format(date, "yyyy-MM-dd") : ""
                              )
                            }
                          />
                        </PopoverContent>
                      </Popover>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                {/* POA Repository — file upload */}
                <FormField
                  control={form.control}
                  name="poa_repository"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>POA Repository</FormLabel>
                      {currentFileUrl && (
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-xs text-muted-foreground">Current:</span>
                          <a
                            href={mediaUrl}
                            target="_blank"
                            rel="noreferrer"
                            className="text-xs font-medium text-primary underline underline-offset-2 hover:text-primary/80"
                          >
                            {currentFileUrl.split("/").pop()}
                          </a>
                        </div>
                      )}
                      <FormControl>
                        <Input
                          type="file"
                          ref={fileRef}
                          onChange={(e) =>
                            field.onChange(e.target.files?.[0] ?? null)
                          }
                        />
                      </FormControl>
                      {currentFileUrl && !field.value && (
                        <p className="text-[11px] text-muted-foreground">
                          Leave empty to keep the current file
                        </p>
                      )}
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

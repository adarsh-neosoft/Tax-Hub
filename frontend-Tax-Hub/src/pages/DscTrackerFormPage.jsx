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
import { Checkbox } from "@/components/ui/checkbox.tsx";
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

const API_PATH = "registration/dsctracker";

export default function DscTrackerFormPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const queryClient = useQueryClient();

  const isEdit = Boolean(id);
  const baseUrl = "dsc-tracker";

  // Fetch Director dropdown options (includes pan for autofill)
  const directorsQuery = useQuery({
    queryKey: ["directors", "dropdown"],
    queryFn: () => api.get("/masters/director/dropdown").then((r) => r.data),
  });

  // Fetch existing record for edit mode
  const recordQuery = useQuery({
    queryKey: ["dsctracker", "record", id],
    queryFn: () => api.get(`/${API_PATH}/${id}/`).then((r) => r.data),
    enabled: isEdit,
  });

  const directors = directorsQuery.data || [];

  const form = useForm({
    defaultValues: {
      name: "",
      pan: "",
      father_name: "",
      from_date: "",
      to_date: "",
      dsc_registered_on_it: false,
    },
  });

  // Populate form when record loads in edit mode
  useEffect(() => {
    if (!recordQuery.data) return;
    form.reset({
      name: recordQuery.data.name ? String(recordQuery.data.name) : "",
      pan: recordQuery.data.pan || "",
      father_name: recordQuery.data.father_name || "",
      from_date: recordQuery.data.from_date || "",
      to_date: recordQuery.data.to_date || "",
      dsc_registered_on_it: Boolean(recordQuery.data.dsc_registered_on_it),
    });
  }, [recordQuery.data, form]);

  // --- Autofill: when name (Director) changes, fill PAN from selected Director ---
  const selectedDirectorId = form.watch("name");

  useEffect(() => {
    if (!selectedDirectorId || !directors.length) {
      form.setValue("pan", "");
      return;
    }

    const director = directors.find(
      (d) => String(d.id) === String(selectedDirectorId)
    );
    if (director) {
      form.setValue("pan", director.pan || "");
    }
  }, [selectedDirectorId, directors, form]);

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
      toast.success(`DSC Tracker ${isEdit ? "updated" : "created"} successfully`);
      queryClient.invalidateQueries({ queryKey: ["dsctracker"] });
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
      // Explicitly include boolean false values so PATCH can unset them
      if (key === "dsc_registered_on_it") {
        payload[key] = value;
        continue;
      }
      payload[key] = value;
    }
    mutation.mutate(payload);
  });

  const isLoading = isEdit && recordQuery.isPending;
  const title = isEdit ? "Edit DSC Tracker" : "Create DSC Tracker";

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
                {/* Name — FK dropdown to Director */}
                <FormField
                  control={form.control}
                  name="name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Name *</FormLabel>
                      <Select
                        onValueChange={field.onChange}
                        value={field.value || ""}
                      >
                        <FormControl>
                          <SelectTrigger className="w-full">
                            <SelectValue placeholder="Select Name" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          {directors.map((dir) => (
                            <SelectItem key={dir.id} value={String(dir.id)}>
                              {dir.director_name}
                            </SelectItem>
                          ))}
                          {!directors.length && (
                            <div className="p-2 text-xs text-muted-foreground">
                              No directors found
                            </div>
                          )}
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                {/* PAN — auto-filled from selected Director */}
                <FormField
                  control={form.control}
                  name="pan"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>PAN</FormLabel>
                      <FormControl>
                        <Input
                          {...field}
                          readOnly
                          placeholder="Auto-filled from Director"
                          className="bg-muted/30"
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                {/* Father's Name */}
                <FormField
                  control={form.control}
                  name="father_name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Father&apos;s Name</FormLabel>
                      <FormControl>
                        <Input {...field} />
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

                {/* DSC registered on IT */}
                <FormField
                  control={form.control}
                  name="dsc_registered_on_it"
                  render={({ field }) => (
                    <FormItem className="flex flex-row items-center gap-3 space-y-0 pt-2">
                      <FormControl>
                        <Checkbox
                          checked={field.value}
                          onCheckedChange={field.onChange}
                        />
                      </FormControl>
                      <FormLabel className="font-normal">
                        Whether DSC registered on IT
                      </FormLabel>
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

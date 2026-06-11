import { useState, useEffect, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { format } from "date-fns";
import { CalendarIcon } from "lucide-react";
import { api } from "iron-stack-ui";
import { FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form.tsx";
import { Input } from "@/components/ui/input.tsx";
import { Textarea } from "@/components/ui/textarea.tsx";
import { Checkbox } from "@/components/ui/checkbox.tsx";
import { Button } from "@/components/ui/button.tsx";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select.tsx";
import { Calendar } from "@/components/ui/calendar.tsx";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover.tsx";
import { cn } from "@/utils/utils.ts";
import { fieldName } from "./formUtils";

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
  if (item.sap_code && item.entity_name) return `${item.sap_code} - ${item.entity_name}`;
  if (item.particular_name) return String(item.particular_name);
  if (item.currency) return String(item.currency);
  return `#${item.id}`;
}

function FkFormField({ control, name, field, disabled }) {
  const [search, setSearch] = useState("");
  const debouncedSearch = useDebounce(search, 300);
  const params = { ...(field.dropdownParams || {}) };
  if (debouncedSearch) params.search = debouncedSearch;

  const { data } = useQuery({
    queryKey: ["dropdown", field.api, params],
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
          <Select disabled={disabled} onValueChange={f.onChange} value={f.value ? String(f.value) : ""}>
            <FormControl>
              <SelectTrigger className="w-full">
                <SelectValue placeholder={`Select ${field.label}`} />
              </SelectTrigger>
            </FormControl>
            <SelectContent>
              <div className="p-2 pb-1">
                <Input
                  placeholder="Search..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="h-8 text-sm"
                  onClick={(e) => e.stopPropagation()}
                  onKeyDown={(e) => e.stopPropagation()}
                />
              </div>
              {(data || []).map((item) => (
                <SelectItem key={item.id} value={String(item.id)}>
                  {getFkLabel(item, field)}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <FormMessage />
        </FormItem>
      )}
    />
  );
}

export default function StageFormFields({ control, sectionKey, fields, disabled, fileUrls = {} }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {fields.map((field) => {
        const name = fieldName(sectionKey, field.key);
        const colSpan = field.type === "textarea" ? "md:col-span-2 lg:col-span-4" : "";

        if (field.type === "fk") {
          return (
            <div key={field.key} className={colSpan}>
              <FkFormField control={control} name={name} field={field} disabled={disabled} />
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
                      <Checkbox disabled={disabled} checked={f.value} onCheckedChange={f.onChange} />
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
                      <Textarea disabled={disabled} placeholder={field.label} {...f} />
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
                            disabled={disabled}
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
          return (
            <div key={field.key} className={colSpan}>
              <FormField
                control={control}
                name={name}
                render={({ field: f }) => (
                  <FormItem>
                    <FormLabel>{field.label}</FormLabel>
                    {current && (
                      <div className="mb-1">
                        <a href={current} target="_blank" rel="noreferrer" className="text-xs text-primary underline">
                          View current file
                        </a>
                      </div>
                    )}
                    <FormControl>
                      <Input
                        type="file"
                        disabled={disabled}
                        onChange={(e) => f.onChange(e.target.files?.[0] ?? null)}
                      />
                    </FormControl>
                  </FormItem>
                )}
              />
            </div>
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
                      type={field.type === "number" ? "number" : "text"}
                      disabled={disabled}
                      placeholder={field.label}
                      {...f}
                      onChange={(e) => f.onChange(e.target.value)}
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

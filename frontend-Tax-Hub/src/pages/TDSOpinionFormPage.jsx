import { useCallback, useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate, useParams, useSearchParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { ArrowLeft } from "lucide-react";
import { toast } from "sonner";
import { api, WorkflowStatus, AuditTrail } from "iron-stack-ui";

import { Form } from "@/components/ui/form.tsx";
import { Button } from "@/components/ui/button.tsx";
import { Card } from "@/components/ui/card.tsx";
import { Badge } from "@/components/ui/badge.tsx";
import { Spinner } from "@/components/ui/spinner.tsx";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion.tsx";
import { useUiConfig } from "@/utils/use-ui-config.js";

import { MASTER_FIELDS, STAGE_FIELD_CONFIG, ALL_SECTION_FIELDS } from "./tds-opinion/fieldConfig";
import StageFormFields from "./tds-opinion/StageFormFields";
import {
  nestedToFormValues,
  sectionFormDefaults,
  buildSectionPayload,
  collectFiles,
} from "./tds-opinion/formUtils";
import { submitWorkflowForm } from "../utils/workflow-form-api.js";

const DEFAULT_STAGES = [
  "Initiated",
  "TDS Opinion",
  "Invoice Posting",
  "Bank Detail",
  "Form 146 Request",
  "Form 145 Request",
  "Payment Details",
  "Close Request",
  "Approved",
];

const DEFAULT_ACCORDION = [
  { stage: "Close Request", key: "close_request", title: "Close Request" },
  { stage: "Payment Details", key: "payment_detail", title: "Payment Details" },
  { stage: "Form 145 Request", key: "form_145", title: "145 Form Request" },
  { stage: "Form 146 Request", key: "form_146", title: "146 Form Request" },
  { stage: "Bank Detail", key: "bank_detail", title: "Bank Details" },
  { stage: "Invoice Posting", key: "invoice_posting", title: "Invoice Posting" },
  { stage: "TDS Opinion", key: "tds_opinion_stage", title: "TDS Opinion" },
  { stage: "Initiated", key: "master", title: "Opinion request" },
];

function ApprovalHierarchy({ stages, currentStage }) {
  const currentIdx = stages.indexOf(currentStage);

  return (
    <Card size="sm" className="p-5 mb-4">
      <h3 className="text-sm font-semibold mb-4">Approval Hierarchy</h3>
      <div className="overflow-x-auto pb-2">
        <div className="flex items-start min-w-max gap-0">
          {stages.map((stage, idx) => {
            const done = idx <= currentIdx;
            return (
              <div key={stage} className="flex items-center">
                <div className="flex flex-col items-center w-28 px-1">
                  <div
                    className={`h-3 w-3 rounded-full border-2 ${
                      done ? "bg-primary border-primary" : "bg-muted border-muted-foreground/30"
                    }`}
                  />
                  <p className={`text-xs text-center mt-2 leading-tight ${done ? "font-medium" : "text-muted-foreground"}`}>
                    {stage}
                  </p>
                </div>
                {idx < stages.length - 1 && (
                  <div className={`h-0.5 w-8 -mt-6 ${idx < currentIdx ? "bg-primary" : "bg-muted"}`} />
                )}
              </div>
            );
          })}
        </div>
      </div>
    </Card>
  );
}

export default function TDSOpinionFormPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const [searchParams] = useSearchParams();
  const queryClient = useQueryClient();
  const { findByPath, navSelectedItem, setNavSelectedItem } = useUiConfig();

  const isEdit = Boolean(id);
  const baseUrl = pathname.split("/").filter(Boolean)[0] || "tds-opinion";
  const pageParam = searchParams.get("page");
  const pageSizeParam = searchParams.get("pageSize");

  const [nestedData, setNestedData] = useState({ master: {} });
  const [stages, setStages] = useState(DEFAULT_STAGES);
  const [accordionSections, setAccordionSections] = useState(DEFAULT_ACCORDION);
  const [editableSections, setEditableSections] = useState(isEdit ? [] : ["master"]);
  const [currentStage, setCurrentStage] = useState("Initiated");
  const [openAccordion, setOpenAccordion] = useState("master");

  const form = useForm({
    defaultValues: sectionFormDefaults(MASTER_FIELDS, "master"),
  });

  useEffect(() => {
    const matched = findByPath("/" + baseUrl);
    if (matched && matched.url !== navSelectedItem?.url) {
      setNavSelectedItem(matched);
    }
  }, [baseUrl, findByPath, navSelectedItem, setNavSelectedItem]);

  const formQuery = useQuery({
    queryKey: ["tds-workflow-form", id],
    queryFn: () => api.get(`/tax_requests/tdsopinion/${id}/workflow-form/`).then((r) => r.data),
    enabled: isEdit,
  });

  useEffect(() => {
    if (!formQuery.data) return;
    const data = formQuery.data.data || { master: {} };
    setNestedData(data);
    setStages(formQuery.data.stages || DEFAULT_STAGES);
    setAccordionSections(formQuery.data.accordion_sections || DEFAULT_ACCORDION);
    setEditableSections(formQuery.data.editable_sections || []);
    const stage = formQuery.data.current_stage || "Initiated";
    setCurrentStage(stage);
    const sections = formQuery.data.accordion_sections || DEFAULT_ACCORDION;
    const section = sections.find((s) => s.stage === stage);
    setOpenAccordion(section?.key || "master");
    form.reset(nestedToFormValues(data));
  }, [formQuery.data, form]);

  const navigateToList = useCallback(() => {
    const params = new URLSearchParams();
    if (pageParam) params.set("page", pageParam);
    if (pageSizeParam) params.set("pageSize", pageSizeParam);
    const qs = params.toString();
    navigate(`/${baseUrl}${qs ? "?" + qs : ""}`, { replace: true });
  }, [navigate, baseUrl, pageParam, pageSizeParam]);

  const saveMutation = useMutation({
    mutationFn: async ({ values, sectionKey }) => {
      const fields =
        sectionKey === "master" ? MASTER_FIELDS : STAGE_FIELD_CONFIG[sectionKey] || [];
      const payload = {
        [sectionKey]: buildSectionPayload(values, sectionKey, fields),
      };
      const files = collectFiles(values);
      const scopedFiles = Object.entries(files).filter(
        ([k]) => !sectionKey || k.startsWith(`${sectionKey}.`),
      );

      const url = isEdit
        ? `/tax_requests/tdsopinion/${id}/workflow-form/`
        : "/tax_requests/tdsopinion/workflow-form/";

      return submitWorkflowForm({
        url,
        method: isEdit ? "patch" : "post",
        payload,
        files: scopedFiles,
      });
    },
    onSuccess: async (res) => {
      toast.success(isEdit ? "Saved successfully" : "Request created");
      await queryClient.invalidateQueries({ queryKey: ["tds-workflow-form"] });
      await queryClient.invalidateQueries({ queryKey: ["TDS Opinion"] });
      await queryClient.invalidateQueries({ queryKey: ["record-workflow"] });

      if (!isEdit) {
        navigateToList();
        return;
      }
      if (res.data) {
        setNestedData(res.data.data);
        setAccordionSections(res.data.accordion_sections || DEFAULT_ACCORDION);
        setEditableSections(res.data.editable_sections || []);
        setCurrentStage(res.data.current_stage || "Initiated");
        form.reset(nestedToFormValues(res.data.data));
      }
    },
    onError: (err) => toast.error(err.response?.data?.detail || "Save failed"),
  });

  const handleBack = useCallback(() => {
    navigateToList();
  }, [navigateToList]);

  const handleClear = () => {
    if (isEdit) {
      form.reset(nestedToFormValues(nestedData));
    } else {
      form.reset(sectionFormDefaults(MASTER_FIELDS, "master"));
    }
  };

  const title = isEdit ? "TDS Opinion" : "Create TDS Opinion";
  const isLoading = isEdit && formQuery.isPending;

  const sectionFieldsMap = useMemo(
    () => ({
      master: MASTER_FIELDS,
      ...STAGE_FIELD_CONFIG,
    }),
    [],
  );

  const submitSection = (sectionKey) => {
    form.handleSubmit((values) => saveMutation.mutate({ values, sectionKey }))();
  };

  const submitCreate = form.handleSubmit(
    (values) => saveMutation.mutate({ values, sectionKey: "master" }),
    () => toast.error("Please check the form and try again."),
  );

  return (
    <div className="p-4">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center">
          <Button variant="ghost" size="icon" onClick={handleBack} className="mr-3">
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h2 className="text-xl font-bold">{title}</h2>
            {nestedData.master?.request_code && (
              <p className="text-sm text-muted-foreground">{nestedData.master.request_code}</p>
            )}
          </div>
        </div>
      </div>

      {isLoading ? (
        <p className="text-sm text-muted-foreground">Loading form…</p>
      ) : !isEdit ? (
        <Card size="sm" className="p-5">
          <h3 className="text-base font-semibold mb-4">Opinion request</h3>
          <Form {...form}>
            <form className="space-y-4" onSubmit={submitCreate}>
              <StageFormFields
                control={form.control}
                sectionKey="master"
                fields={MASTER_FIELDS}
                disabled={false}
                fileUrls={{}}
              />
              <div className="flex justify-end gap-2 pt-4 border-t">
                <Button type="button" variant="ghost" onClick={handleClear} disabled={saveMutation.isPending}>
                  Clear
                </Button>
                <Button type="submit" disabled={saveMutation.isPending}>
                  {saveMutation.isPending && <Spinner className="mr-2" />}
                  Submit
                </Button>
              </div>
            </form>
          </Form>
        </Card>
      ) : (
        <>
          <ApprovalHierarchy stages={stages} currentStage={currentStage} />

          <Card size="sm" className="p-5 mb-4">
            <Accordion type="single" collapsible value={openAccordion} onValueChange={setOpenAccordion}>
              {accordionSections.map((section) => {
                const fields = sectionFieldsMap[section.key] || [];
                const editable = editableSections.includes(section.key);
                const fileUrls = nestedData[section.key] || {};

                return (
                  <AccordionItem key={section.key} value={section.key}>
                    <AccordionTrigger className="text-base font-medium hover:no-underline">
                      <div className="flex items-center gap-2">
                        <span>{section.title}</span>
                        {section.stage === currentStage && (
                          <Badge variant="default" className="text-xs">Current</Badge>
                        )}
                        {!editable && <Badge variant="secondary" className="text-xs">Read only</Badge>}
                      </div>
                    </AccordionTrigger>
                    <AccordionContent className="pt-2 pb-4">
                      <Form {...form}>
                        <form className="space-y-4" onSubmit={(e) => e.preventDefault()}>
                          <StageFormFields
                            control={form.control}
                            sectionKey={section.key}
                            fields={fields}
                            disabled={!editable}
                            fileUrls={fileUrls}
                          />
                          {editable && (
                            <div className="flex justify-end gap-2 pt-4 border-t">
                              <Button
                                type="button"
                                variant="outline"
                                onClick={handleClear}
                                disabled={saveMutation.isPending}
                              >
                                Cancel
                              </Button>
                              <Button
                                type="button"
                                onClick={() => submitSection(section.key)}
                                disabled={saveMutation.isPending}
                              >
                                {saveMutation.isPending && <Spinner className="mr-2" />}
                                Save
                              </Button>
                            </div>
                          )}
                        </form>
                      </Form>
                    </AccordionContent>
                  </AccordionItem>
                );
              })}
            </Accordion>
          </Card>

          <WorkflowStatus appLabel="tax_requests" modelName="tdsopinion" objectId={id} />
          <AuditTrail appLabel="tax_requests" modelName="tdsopinion" objectId={id} />
        </>
      )}
    </div>
  );
}

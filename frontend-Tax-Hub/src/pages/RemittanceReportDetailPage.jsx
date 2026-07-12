import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { ArrowLeft } from "lucide-react";
import { toast } from "sonner";
import { api, WorkflowStatus, AuditTrail } from "iron-stack-ui";

import { Button } from "@/components/ui/button.tsx";

import { MASTER_FIELDS, STAGE_FIELD_CONFIG } from "./tds-opinion/fieldConfig";
import {
  nestedToFormValues,
  buildSectionPayload,
  collectFiles,
} from "./tds-opinion/formUtils";
import { submitWorkflowForm } from "../utils/workflow-form-api.js";
import ApprovalHierarchy from "./ApprovalHierarchy.jsx";
import WorkflowAccordion from "./WorkflowAccordion.jsx";

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

export default function RemittanceReportDetailPage() {
  const { id: remittanceId } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  // Fetch the RemittanceReport to get the linked TDSOpinion ID
  const remittanceQuery = useQuery({
    queryKey: ["remittance-report", remittanceId],
    queryFn: () => api.get(`/reports/remittancereport/${remittanceId}/`).then((r) => r.data),
    enabled: Boolean(remittanceId),
  });

  const tdsOpinionId = remittanceQuery.data?.tds_opinion;

  // Fetch the TDS Opinion workflow form data
  const formQuery = useQuery({
    queryKey: ["tds-workflow-form", tdsOpinionId],
    queryFn: () =>
      api.get(`/tax_requests/tdsopinion/${tdsOpinionId}/workflow-form/`).then((r) => r.data),
    enabled: Boolean(tdsOpinionId),
    refetchOnWindowFocus: true,
    staleTime: 0,
  });

  const [nestedData, setNestedData] = useState({ master: {} });
  const [stages, setStages] = useState(DEFAULT_STAGES);
  const [accordionSections, setAccordionSections] = useState(DEFAULT_ACCORDION);
  const [editableSections, setEditableSections] = useState([]);
  const [currentStage, setCurrentStage] = useState("Initiated");
  const [openAccordion, setOpenAccordion] = useState("master");

  const form = useForm({ defaultValues: {} });

  // Populate form when workflow data is loaded
  useEffect(() => {
    if (!formQuery.data) return;
    const data = formQuery.data.data || { master: {} };
    const formValues = nestedToFormValues(data);
    setNestedData(data);
    setStages(formQuery.data.stages || DEFAULT_STAGES);
    setAccordionSections(formQuery.data.accordion_sections || DEFAULT_ACCORDION);
    setEditableSections(formQuery.data.editable_sections || []);
    const stage = formQuery.data.current_stage || "Initiated";
    setCurrentStage(stage);
    const sections = formQuery.data.accordion_sections || DEFAULT_ACCORDION;
    const section = sections.find((s) => s.stage === stage);
    setOpenAccordion(section?.key || "master");
    form.reset(formValues);
  }, [formQuery.data, form]);

  const poNpo = form.watch("master.po_npo");
  const form146Type = form.watch("bank_detail.form_146_type");

  const { data: form146TypeData } = useQuery({
    queryKey: ["type15cb", form146Type],
    enabled: !!form146Type,
    queryFn: async () => {
      const response = await api.get(`/masters/type15cb/${form146Type}/`);
      return response.data;
    },
  });

  // Save mutation
  const saveMutation = useMutation({
    mutationFn: async ({ values, sectionKey }) => {
      const fields =
        sectionKey === "master" ? MASTER_FIELDS : STAGE_FIELD_CONFIG[sectionKey] || [];
      const payload = {
        [sectionKey]: buildSectionPayload(values, sectionKey, fields),
      };

      const files = collectFiles(values);
      const scopedFiles = Object.entries(files).filter(
        ([k]) => !sectionKey || k.startsWith(`${sectionKey}.`)
      );

      return submitWorkflowForm({
        url: `/tax_requests/tdsopinion/${tdsOpinionId}/workflow-form/`,
        method: "patch",
        payload,
        files: scopedFiles,
      });
    },
    onSuccess: async (res) => {
      toast.success("Saved successfully");
      await queryClient.invalidateQueries({ queryKey: ["tds-workflow-form"] });
      await queryClient.invalidateQueries({ queryKey: ["TDS Opinion"] });
      await queryClient.invalidateQueries({ queryKey: ["record-workflow"] });

      if (res.data) {
        setNestedData(res.data.data);
        setAccordionSections(res.data.accordion_sections || DEFAULT_ACCORDION);
        setEditableSections(res.data.editable_sections || []);
        setCurrentStage(res.data.current_stage || "Initiated");
        form.reset(nestedToFormValues(res.data.data));
      }
    },
    onError: (error) => {
      const detail = error?.response?.data?.detail || "Save failed";
      toast.error(detail);
    },
  });

  // Auto-save
  const autoSaveTimerRef = useRef(null);
  const dirtySectionsRef = useRef(new Set());

  useEffect(() => {
    if (!tdsOpinionId) return;

    const subscription = form.watch((values, info) => {
      if (!info?.name || !info?.type) return;
      const parts = info.name.split(".");
      if (parts.length < 2) return;
      const sectionKey = parts[0];

      if (!editableSectionsRef.current.includes(sectionKey)) return;

      const fields = sectionKey === "master" ? MASTER_FIELDS : STAGE_FIELD_CONFIG[sectionKey] || [];
      const fieldDef = fields.find((f) => f.key === parts[1]);
      if (fieldDef?.disabled) return;

      dirtySectionsRef.current.add(sectionKey);

      if (autoSaveTimerRef.current) clearTimeout(autoSaveTimerRef.current);
      autoSaveTimerRef.current = setTimeout(() => {
        const sectionsToSave = [...dirtySectionsRef.current];
        dirtySectionsRef.current = new Set();
        sectionsToSave.forEach((sk) => {
          if (!saveMutation.isPending) {
            saveMutation.mutate({ values: form.getValues(), sectionKey: sk, _skipToast: true });
          }
        });
      }, 1500);
    });

    return () => {
      subscription.unsubscribe();
      if (autoSaveTimerRef.current) clearTimeout(autoSaveTimerRef.current);
    };
  }, [form, tdsOpinionId]); // eslint-disable-line react-hooks/exhaustive-deps

  const editableSectionsRef = useRef(editableSections);
  editableSectionsRef.current = editableSections;

  const handleBack = useCallback(() => {
    navigate("/remittance-report", { replace: true });
  }, [navigate]);

  const requestCode = nestedData.master?.request_code;
  const isLoading = remittanceQuery.isPending || formQuery.isPending;

  const sectionFieldsMap = useMemo(
    () => ({
      master: MASTER_FIELDS,
      ...STAGE_FIELD_CONFIG,
    }),
    []
  );

  if (isLoading) {
    return (
      <div className="p-4">
        <p className="text-sm text-muted-foreground">Loading request details…</p>
      </div>
    );
  }

  if (!tdsOpinionId) {
    return (
      <div className="p-4">
        <div className="flex items-center mb-4">
          <Button variant="ghost" size="icon" onClick={handleBack} className="mr-3">
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <h2 className="text-xl font-bold">Remittance Report</h2>
        </div>
        <p className="text-sm text-muted-foreground">No linked TDS Opinion found for this record.</p>
      </div>
    );
  }

  return (
    <div className="p-4">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center">
          <Button variant="ghost" size="icon" onClick={handleBack} className="mr-3">
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h2 className="text-xl font-bold">Remittance Report</h2>
            {requestCode && (
              <p className="text-sm text-muted-foreground">{requestCode}</p>
            )}
          </div>
        </div>
      </div>

      <ApprovalHierarchy stages={stages} currentStage={currentStage} />

      <WorkflowAccordion
        form={form}
        accordionSections={accordionSections}
        sectionFieldsMap={sectionFieldsMap}
        editableSections={editableSections}
        currentStage={currentStage}
        openAccordion={openAccordion}
        setOpenAccordion={setOpenAccordion}
        queryClient={queryClient}
        form146TypeData={form146TypeData}
        poNpo={poNpo}
        requestId={tdsOpinionId}
        sectionFields={nestedData}
      />

      <WorkflowStatus appLabel="tax_requests" modelName="tdsopinion" objectId={tdsOpinionId} />
      {/* <AuditTrail appLabel="tax_requests" modelName="tdsopinion" objectId={tdsOpinionId} /> */}
    </div>
  );
}

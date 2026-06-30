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
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog.tsx";
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

// Mapping of master file fields to their corresponding valid_upto date fields
const FILE_VALIDITY_MAP = {
  form_10f_file: "form_10f_valid_upto",
  trc_file: "trc_valid_upto",
  contract_agreement_copy: "agreement_valid_upto",
  pan_file: "pan_valid_upto",
  no_pe_declaration_file: "no_pe_valid_upto",
  proof_of_reimbursement_file: "reimbursement_valid_upto",
};

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

  const bankIfscCode = form.watch("bank_detail.bank_ifsc_code");
  const form146Type = form.watch("bank_detail.form_146_type");

  const invoiceValueFc = form.watch("tds_opinion_stage.invoice_value_fc");
  const assesseableValueFc = form.watch("tds_opinion_stage.assesseable_value_fc");
  const exchangeRate = form.watch("tds_opinion_stage.exchange_rate");
  const taxRate = form.watch("tds_opinion_stage.tax_rate");
  const grossingUpApplicable = form.watch("tds_opinion_stage.grossing_up_applicable");
  const poNpo = form.watch("master.po_npo");
  const particular = form.watch("master.particular");
  const [particularOptions, setParticularOptions] = useState([]);
  const company = form.watch("master.company");
  const vendor = form.watch("master.vendor");

  const [existingRequestData, setExistingRequestData] = useState(null);
  const [showVendorNoteDialog, setShowVendorNoteDialog] = useState(false);
  const [validFileUrls, setValidFileUrls] = useState({});
  const [copyFileFields, setCopyFileFields] = useState([]);
  const [removedFileFields, setRemovedFileFields] = useState(new Set());
  const invoiceDate = form.watch("master.invoice_date");

  useEffect(() => {
    const subscription = form.watch((values, info) => {
    });

    return () => subscription.unsubscribe();
  }, [form]);

  useEffect(() => {
    if (!company || !vendor || isEdit) return;

    const timer = setTimeout(async () => {
      try {
        const res = await api.get(
          `/tax_requests/tdsopinion/check-existing/`,
          {
            params: {
              company,
              vendor,
            },
          }
        );

        if (res.data?.exists) {
          setExistingRequestData(res.data);
          setShowVendorNoteDialog(true);

          if (res.data.pan_number) {
            form.setValue(
              "master.pan_number",
              res.data.pan_number
            );
          }

          if (res.data.tin_number) {
            form.setValue(
              "master.tin_number",
              res.data.tin_number
            );
          }
        } else {
          setExistingRequestData(null);
          setValidFileUrls({});
          setCopyFileFields([]);
        }
      } catch (e) {
        console.error(e);
      }
    }, 500);

    return () => clearTimeout(timer);
  }, [company, vendor]);

  // Filter out removed files from the pre-populated URLs
  const filteredFileUrls = useMemo(() => {
    const filtered = {};
    for (const [key, url] of Object.entries(validFileUrls)) {
      if (!removedFileFields.has(key)) {
        filtered[key] = url;
      }
    }
    return filtered;
  }, [validFileUrls, removedFileFields]);

  const handleRemoveCopiedFile = useCallback((fieldKey) => {
    setRemovedFileFields(prev => {
      const next = new Set(prev);
      next.add(fieldKey);
      return next;
    });
    // Also clear the corresponding valid_upto date field
    const uptoField = FILE_VALIDITY_MAP[fieldKey];
    if (uptoField) {
      form.setValue(`master.${uptoField}`, "");
    }
  }, [form]);

  // Fields that are actively being copied (not removed by user)
  const activeCopyFields = useMemo(
    () => copyFileFields.filter(f => !removedFileFields.has(f)),
    [copyFileFields, removedFileFields]
  );

  // When invoice_date changes, fetch valid files from the existing request
  useEffect(() => {
    if (!existingRequestData?.request_id || !invoiceDate || isEdit) {
      if (!existingRequestData) {
        setValidFileUrls({});
        setCopyFileFields([]);
        setRemovedFileFields(new Set());
      }
      return;
    }

    setRemovedFileFields(new Set());

    const timer = setTimeout(async () => {
      try {
        const res = await api.get(
          `/tax_requests/tdsopinion/check-existing/`,
          {
            params: {
              company,
              vendor,
              invoice_date: invoiceDate,
            },
          }
        );

        if (res.data?.valid_files) {
          setValidFileUrls(res.data.valid_files);
          setCopyFileFields(res.data.valid_file_fields || []);

          // Populate the corresponding valid_upto date fields from the existing request
          const uptoDates = res.data.valid_file_upto_dates || {};
          Object.entries(uptoDates).forEach(([fileField, dateValue]) => {
            const uptoField = FILE_VALIDITY_MAP[fileField];
            if (uptoField && dateValue) {
              form.setValue(`master.${uptoField}`, dateValue);
            }
          });
        } else {
          setValidFileUrls({});
          setCopyFileFields([]);
        }
      } catch (e) {
        console.error(e);
        setValidFileUrls({});
        setCopyFileFields([]);
      }
    }, 500);

    return () => clearTimeout(timer);
  }, [invoiceDate, existingRequestData, company, vendor, isEdit]);

  useEffect(() => {
    const invoiceFc = parseFloat(invoiceValueFc || 0);
    const assessFc = parseFloat(assesseableValueFc || 0);
    const rate = parseFloat(exchangeRate || 0);
    const tdsRate = parseFloat(taxRate || 0);

    const invoiceInr = invoiceFc * rate;
    const assessInr = assessFc * rate;

    let tdsFc = 0;
    let tdsInr = 0;

    if (grossingUpApplicable) {
      tdsFc =
        tdsRate > 0
          ? (assessFc / (1 - tdsRate / 100)) * (tdsRate / 100)
          : 0;

      tdsInr =
        tdsRate > 0
          ? (assessInr / (1 - tdsRate / 100)) * (tdsRate / 100)
          : 0;
    } else {
      tdsFc = assessFc * (tdsRate / 100);
      tdsInr = assessInr * (tdsRate / 100);
    }

    const netPayableFc = grossingUpApplicable
      ? invoiceFc
      : invoiceFc - tdsFc;

    const netPayableInr = grossingUpApplicable
      ? invoiceInr
      : invoiceInr - tdsInr;

    form.setValue(
      "tds_opinion_stage.invoice_value_inr",
      invoiceInr.toFixed(2),
      { shouldDirty: true, shouldValidate: true }
    );

    form.setValue(
      "tds_opinion_stage.assesseable_value_inr",
      assessInr.toFixed(2),
      { shouldDirty: true, shouldValidate: true }
    );

    form.setValue(
      "tds_opinion_stage.tds_amount_fc",
      tdsFc.toFixed(2),
      { shouldDirty: true, shouldValidate: true }
    );

    form.setValue(
      "tds_opinion_stage.tds_amount_inr",
      tdsInr.toFixed(2),
      { shouldDirty: true, shouldValidate: true }
    );

    form.setValue(
      "tds_opinion_stage.net_payable_fc",
      netPayableFc.toFixed(2),
      { shouldDirty: true, shouldValidate: true }
    );

    form.setValue(
      "tds_opinion_stage.net_payable_inr",
      netPayableInr.toFixed(2),
      { shouldDirty: true, shouldValidate: true }
    );

  }, [
    invoiceValueFc,
    assesseableValueFc,
    exchangeRate,
    taxRate,
    grossingUpApplicable,
    form,
  ]);

  useEffect(() => {
    const matched = findByPath("/" + baseUrl);
    if (matched && matched.url !== navSelectedItem?.url) {
      setNavSelectedItem(matched);
    }
  }, [baseUrl, findByPath, navSelectedItem, setNavSelectedItem]);

  useEffect(() => {

    if (!bankIfscCode) return;

    const fetchBank = async () => {

      try {

        const response = await api.get(
          `/masters/bank/${bankIfscCode}/`
        );

        const bank = response.data;

        form.setValue(
          "bank_detail.bank_name",
          bank.bank_name || ""
        );

        form.setValue(
          "bank_detail.branch_name",
          bank.branch_name || ""
        );

        form.setValue(
          "bank_detail.bsr_code",
          bank.bsr_code || ""
        );

        form.setValue(
          "bank_detail.itdrein",
          bank.itdrein || ""
        );

      } catch (error) {
        console.error(error);
      }
    };

    fetchBank();

  }, [bankIfscCode, form]);

  useEffect(() => {
    const fetchParticulars = async () => {
      try {
        const response = await api.get(
          "/masters/particular/dropdown"
        );

        setParticularOptions(response.data.results || []);
      } catch (error) {
        console.error(error);
      }
    };

    fetchParticulars();
  }, []);

  const { data: form146TypeData } = useQuery({
    queryKey: ["type15cb", form146Type],
    enabled: !!form146Type,
    queryFn: async () => {
      const response = await api.get(
        `/masters/type15cb/${form146Type}/`
      );

      return response.data;
    },
  });

  const formQuery = useQuery({
    queryKey: ["tds-workflow-form", id],
    queryFn: () =>
      api.get(`/tax_requests/tdsopinion/${id}/workflow-form/`)
        .then((r) => r.data),
    enabled: isEdit,

    refetchOnWindowFocus: true,
    staleTime: 0,
  });

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

      // If creating a new form and we have files to copy from an existing request
      if (!isEdit && sectionKey === "master" && existingRequestData?.request_id && activeCopyFields.length > 0) {
        payload[sectionKey]._copy_files_from = existingRequestData.request_id;
        payload[sectionKey]._copy_file_fields = activeCopyFields;
      }

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
    onError: (error) => {
      const detail = error?.response?.data?.detail || "";

      form.clearErrors();

      const fieldMap = {
        form_10f_file: "Electronically filed Form 10F",
        no_pe_declaration_file: "No PE Declaration",
        trc_file: "Tax Residency Certificate (TRC)",
        contract_agreement_copy: "Contract Agreement Copy",
        proof_of_reimbursement_file: "Proof of reimbursement claims",
      };

      Object.entries(fieldMap).forEach(([backendField, label]) => {
        if (detail.includes(backendField)) {
          form.setError(`master.${backendField}`, {
            type: "manual",
            message: `${label} is required`,
          });
        console.log(
          backendField,
          form.getFieldState(`master.${backendField}`)
        );
        }
      });

      setTimeout(() => {
        console.log(form.formState.errors);
      }, 100);

      toast.error(detail || "Please fill all required fields.");
    },
    // onError: (err) => toast.error(err.response?.data?.detail || "Save failed"),
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

  const notesData = [
    {
      particular: "Electronically filed form 10F",
      details:
        "It is auto generated form which can be downloaded by vendor via login on Income Tax portal; Sample Format Attached.",
    },
    {
      particular: "No PE declaration",
      details:
        "No PE Declaration is a certificate provided by a non-resident on his letterhead stating that he doesn't have any permanent establishment in INDIA. PE here broadly covers project PE, service PE, branch PE etc.",
    },
    {
      particular: "Tax Residency Certificate",
      details:
        "TRC is a document/certification issued by the tax authorities of the country of the person, confirming that such person is a resident of such country in that particular financial year. In brevity, TRC is proof of residency.",
    },
    {
      particular: "PAN",
      details: "This document is mandatory if the non-resident obtains PAN in INDIA",
    },
    {
      particular: "Form 145 and Form 146 both not required",
      details: "Goods of Supply;",
    },
    {
      particular: "Only Form 145 Required (Form 146 not required)",
      details:
        "LDC-Part-B: 2. Reimbursement-Part-D; 3. Any Other Income not taxable under Income tax act-Part-D.",
    },
  ];

  const title = isEdit ? "TDS Opinion" : "Create TDS Opinion";
  const isLoading = isEdit && formQuery.isPending;

  const sectionFieldsMap = useMemo(
    () => ({
      master: MASTER_FIELDS,
      ...STAGE_FIELD_CONFIG,
    }),
    [],
  );

  const validateParticularDocuments = (values) => {
    const master = values.master || {};

    form.clearErrors([
      "master.form_10f_file",
      "master.no_pe_declaration_file",
      "master.trc_file",
      "master.contract_agreement_copy",
      "master.proof_of_reimbursement_file",
    ]);

    const errors = [];

    const selectedParticular = particularOptions.find(
      (item) => String(item.id) === String(master.particular)
    );

    const particularName = (
      selectedParticular?.particular_name || ""
    )
      .trim()
      .toLowerCase();

    // Helper: check if a field has a file being copied from existing request
    const hasCopiedFile = (fieldKey) => activeCopyFields.includes(fieldKey);

    if (particularName === "supply of goods") {
      if (!master.no_pe_declaration_file && !hasCopiedFile("no_pe_declaration_file")) {
        form.setError("master.no_pe_declaration_file", {
          type: "required",
          message: "No PE Declaration is required",
        });

        errors.push("No PE Declaration is required");
      }
    }

    if (particularName === "supply of services") {
      if (!master.form_10f_file && !hasCopiedFile("form_10f_file")) {
        form.setError("master.form_10f_file", {
          type: "required",
          message: "Form 10F is required",
        });

        errors.push("Form 10F is required");
      }

      if (!master.no_pe_declaration_file && !hasCopiedFile("no_pe_declaration_file")) {
        form.setError("master.no_pe_declaration_file", {
          type: "required",
          message: "No PE Declaration is required",
        });

        errors.push("No PE Declaration is required");
      }

      if (!master.trc_file && !hasCopiedFile("trc_file")) {
        form.setError("master.trc_file", {
          type: "required",
          message: "TRC file is required",
        });

        errors.push("TRC file is required");
      }

      if (!master.contract_agreement_copy && !hasCopiedFile("contract_agreement_copy")) {
        form.setError("master.contract_agreement_copy", {
          type: "required",
          message: "Contract Agreement Copy is required",
        });

        errors.push("Contract Agreement Copy is required");
      }
    }

    if (
      particularName.includes("pure reimbursement") ||
      particularName.includes("any other income")
    ) {
      if (!master.proof_of_reimbursement_file && !hasCopiedFile("proof_of_reimbursement_file")) {
        form.setError("master.proof_of_reimbursement_file", {
          type: "required",
          message: "Proof of reimbursement claims is required",
        });

        errors.push("Proof of reimbursement claims is required");
      }
    }

    return errors;
  };

  const submitSection = (sectionKey) => {
    form.handleSubmit((values) => {

      if (sectionKey === "master") {
        const errors = validateParticularDocuments(values);

        if (errors.length) {
          toast.error(
          <div className="space-y-1">
            {errors.map((error, index) => (
              <div key={index}>{error}</div>
            ))}
          </div>
        );
          return;
        }
      }

      saveMutation.mutate({
        values,
        sectionKey,
      });

    })();
  };

  const submitCreate = form.handleSubmit(
    (values) => {
      const errors = validateParticularDocuments(values);

      if (errors.length) {
        toast.error(
        <div className="space-y-1">
          {errors.map((error, index) => (
            <div key={index}>{error}</div>
          ))}
        </div>
      );
        return;
      }

      saveMutation.mutate({
        values,
        sectionKey: "master",
      });
    },
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
                fields={
                  poNpo
                    ? MASTER_FIELDS
                    : MASTER_FIELDS.filter(
                        (field) => field.key !== "po_number"
                      )
                }
                disabled={false}
                fileUrls={filteredFileUrls}
                requestId={id}
                values={form.watch()}
                onRemoveCopiedFile={handleRemoveCopiedFile}
                copiedFileFields={copyFileFields}
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
                            fields={
                              section.key === "bank_detail"
                                ? fields.filter((field) => {
                                    const selectedType = (
                                      form146TypeData?.type_15cb || ""
                                    ).toLowerCase();

                                    const showExternalCA =
                                      selectedType.includes("146") &&
                                      selectedType.includes("part c");

                                    if (
                                      field.key === "external_ca" &&
                                      !showExternalCA
                                    ) {
                                      return false;
                                    }

                                    return true;
                                  })
                                : section.key === "master" && !poNpo
                                  ? fields.filter(
                                      (field) => field.key !== "po_number"
                                    )
                                  : fields
                            }
                            disabled={!editable}
                            fileUrls={fileUrls}
                            requestId={id}
                            values={form.watch()}
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

      <Dialog open={showVendorNoteDialog} onOpenChange={setShowVendorNoteDialog}>
        <DialogContent className="sm:max-w-2xl max-h-[85vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="text-lg font-bold">Note</DialogTitle>
            <DialogDescription>
              {existingRequestData && (
                <div className="bg-muted/50 rounded-md p-3 mb-4 text-sm space-y-1">
                  <p>
                    <span className="font-semibold">Request ID:</span>{" "}
                    {existingRequestData.request_id}
                  </p>
                  {existingRequestData.pan_number && (
                    <p>
                      <span className="font-semibold">Existing PAN Number:</span>{" "}
                      {existingRequestData.pan_number}
                    </p>
                  )}
                  {existingRequestData.tin_number && (
                    <p>
                      <span className="font-semibold">Existing TIN Number:</span>{" "}
                      {existingRequestData.tin_number}
                    </p>
                  )}
                </div>
              )}
            </DialogDescription>
          </DialogHeader>

          <div className="overflow-x-auto">
            <table className="w-full border-collapse text-sm">
              <thead>
                <tr className="bg-muted/50">
                  <th className="border px-3 py-2 text-left font-semibold w-1/3">
                    Particulars
                  </th>
                  <th className="border px-3 py-2 text-left font-semibold">
                    Details
                  </th>
                </tr>
              </thead>
              <tbody>
                {notesData.map((row, idx) => (
                  <tr key={idx} className="border-b">
                    <td className="border px-3 py-2.5 font-medium text-muted-foreground align-top">
                      {row.particular}
                    </td>
                    <td className="border px-3 py-2.5 text-muted-foreground">
                      {row.details}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <DialogFooter>
            <Button
              type="button"
              onClick={() => setShowVendorNoteDialog(false)}
            >
              OK
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
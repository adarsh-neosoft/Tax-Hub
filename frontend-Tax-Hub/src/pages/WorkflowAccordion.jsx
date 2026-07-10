import { useState } from "react";
import { Form } from "@/components/ui/form.tsx";
import { Card } from "@/components/ui/card.tsx";
import { Badge } from "@/components/ui/badge.tsx";
import { Button } from "@/components/ui/button.tsx";
import { Spinner } from "@/components/ui/spinner.tsx";
import { Textarea } from "@/components/ui/textarea.tsx";
import { CheckCircle, XCircle, RotateCcw } from "lucide-react";

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion.tsx";

import StageFormFields from "./tds-opinion/StageFormFields";

export default function WorkflowAccordion({
    form,
    accordionSections,
    sectionFieldsMap,
    editableSections,
    currentStage,
    openAccordion,
    setOpenAccordion,
    queryClient,
    form146TypeData,
    poNpo,
    fileUrls,
    requestId,
    sectionFields,
    saveMutation,
    approvalMode,
    workflow,            // { instance_id, status, can_act, allow_return, allow_resubmission }
    onWorkflowAction,    // (action, comment, sectionKey) => void
    pendingAction,       // Currently running action: "approve" | "reject" | "return" | null
}) {

    // Track comments per section key — state lifted out of the map loop
    const [comments, setComments] = useState({});

    const setComment = (sectionKey, value) => {
        setComments(prev => ({ ...prev, [sectionKey]: value }));
    };

    // Derive fields from data keys when sectionFieldsMap is not provided (e.g. approval mode)
    const deriveFields = (sectionKey) => {
        if (sectionFieldsMap) {
            return sectionFieldsMap[sectionKey] || [];
        }
        // Fallback: generate basic field definitions from the data keys
        const data = sectionFields?.[sectionKey];
        if (!data) return [];
        return Object.keys(data).map((key) => ({
            key,
            // If the value looks like a url/object, treat as file
            type: (typeof data[key] === "object" && data[key] !== null && !Array.isArray(data[key]))
                ? "file"
                : "text",
        }));
    };

    return (
        <Card size="sm" className="p-5 mb-4">
                    <Accordion type="single" collapsible value={openAccordion} onValueChange={setOpenAccordion}>
                      {accordionSections.map((section) => {
                        const fields = deriveFields(section.key);
                        const editable = editableSections.includes(section.key);
                        const sectionFileUrls = sectionFields?.[section.key] || {};

                        // Determine if this section should show action buttons
                        const isCurrentStageSection = section.stage === currentStage;
                        const canAct = workflow?.can_act === true;
                        const showActions = editable && isCurrentStageSection && canAct;

                        // Get comment for this section
                        const comment = comments[section.key] || "";

                        // In approval mode or when form146TypeData/poNpo not available, skip special field filtering
                        const useFormFiltering = !approvalMode && sectionFieldsMap;

                        let filteredFields = fields;

                        if (useFormFiltering && section.key === "bank_detail") {
                            filteredFields = fields.filter((field) => {
                                const selectedType = (
                                    form146TypeData?.type_15cb || ""
                                ).toLowerCase();

                                const showExternalCA =
                                    selectedType.includes("146") &&
                                    selectedType.includes("part c");

                                if (field.key === "external_ca" && !showExternalCA) {
                                    return false;
                                }

                                return true;
                            });
                        } else if (useFormFiltering && section.key === "master" && !poNpo) {
                            filteredFields = fields.filter(
                                (field) => field.key !== "po_number"
                            );
                        }
        
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
                                    fields={filteredFields}
                                    disabled={!editable}
                                    fileUrls={sectionFileUrls}
                                    requestId={requestId}
                                    values={form.watch()}
                                    onComparisonComplete={() => {
                                        queryClient?.invalidateQueries({ queryKey: ["tds-workflow-form", requestId] });
                                        queryClient?.invalidateQueries({ queryKey: ["approval"] });
                                    }}
                                  />
                                  {showActions && (
                                    <div className="space-y-3 pt-4 border-t">
                                      <Textarea
                                        placeholder="Add a comment (optional)..."
                                        value={comment}
                                        onChange={(e) => setComment(section.key, e.target.value)}
                                        className="min-h-[50px] text-sm"
                                      />
                                      <div className="flex gap-2">
                                        <Button
                                          type="button"
                                          size="sm"
                                          className="bg-green-600 hover:bg-green-700 text-white"
                                          onClick={() => {
                                            onWorkflowAction("approve", comment, section.key);
                                            setComment(section.key, "");
                                          }}
                                          disabled={!!pendingAction}
                                        >
                                          {pendingAction === "approve" && <Spinner className="mr-1 h-3 w-3" />}
                                          <CheckCircle className="h-3.5 w-3.5 mr-1" />
                                          Approve
                                        </Button>
                                        <Button
                                          type="button"
                                          size="sm"
                                          variant="destructive"
                                          onClick={() => {
                                            onWorkflowAction("reject", comment, section.key);
                                            setComment(section.key, "");
                                          }}
                                          disabled={!!pendingAction}
                                        >
                                          {pendingAction === "reject" && <Spinner className="mr-1 h-3 w-3" />}
                                          <XCircle className="h-3.5 w-3.5 mr-1" />
                                          Reject
                                        </Button>
                                        {workflow?.allow_return && (
                                          <Button
                                            type="button"
                                            size="sm"
                                            variant="outline"
                                            onClick={() => {
                                              onWorkflowAction("return", comment, section.key);
                                              setComment(section.key, "");
                                            }}
                                            disabled={!!pendingAction}
                                          >
                                            {pendingAction === "return" && <Spinner className="mr-1 h-3 w-3" />}
                                            <RotateCcw className="h-3.5 w-3.5 mr-1" />
                                            Return
                                          </Button>
                                        )}
                                      </div>
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
    );
}
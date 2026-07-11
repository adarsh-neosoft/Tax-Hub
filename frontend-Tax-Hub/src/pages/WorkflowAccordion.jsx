import { Form } from "@/components/ui/form.tsx";
import { Card } from "@/components/ui/card.tsx";
import { Badge } from "@/components/ui/badge.tsx";

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
    approvalMode,
    approvalToken,
}) {

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
                                    approvalMode={approvalMode}
                                    approvalToken={approvalToken}
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
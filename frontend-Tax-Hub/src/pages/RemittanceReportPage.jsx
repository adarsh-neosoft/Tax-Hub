import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { AgGridReact } from "ag-grid-react";
import { toast } from "sonner";

import { api, useGridDatasource, ListViewHeader, gridTheme } from "iron-stack-ui";
import { useUiConfig } from "@/utils/use-ui-config.js";

import { Button } from "@/components/ui/button.tsx";
import { Card } from "@/components/ui/card.tsx";

const DEFAULT_PAGE_SIZE = 20;

const DEFAULT_COLUMNS = [
  { headerName: "Request ID", field: "request_id", filter: "agTextColumnFilter" },
  { headerName: "Vendor Name", field: "vendor_name", filter: "agTextColumnFilter" },
  { headerName: "Vendor Code", field: "vendor_code", filter: "agTextColumnFilter" },
  { headerName: "Gross Amt-INR", field: "gross_amount_inr", filter: "agNumberColumnFilter" },
  { headerName: "TDS Amt-INR", field: "tds_amount_inr", filter: "agNumberColumnFilter" },
  { headerName: "Net Amount-INR", field: "net_amount_inr", filter: "agNumberColumnFilter" },
  { headerName: "SAP Document No.", field: "sap_document_number", filter: "agTextColumnFilter" },
  { headerName: "Invoice Number", field: "invoice_number", filter: "agTextColumnFilter" },
  { headerName: "Status", field: "status", filter: "agTextColumnFilter" },
  { headerName: "Form 145 Ackn.", field: "form_145_ack_number", filter: "agTextColumnFilter" },
  { headerName: "Form 146 Ackn.", field: "form_146_ack_number", filter: "agTextColumnFilter" },
  { headerName: "Payment Doc. No.", field: "payment_document_number", filter: "agTextColumnFilter" },
  { headerName: "Payment Date", field: "payment_date", filter: "agDateColumnFilter" },
];

// File attachment columns — rendered as clickable links
const FILE_COLUMNS = [
  { headerName: "Form 145", field: "form_145_attachment" },
  { headerName: "Form 146", field: "form_146_attachment" },
  { headerName: "TRC", field: "trc_attachment" },
  { headerName: "NO PE", field: "no_pe_attachment" },
  { headerName: "Form 10F", field: "form_10f_attachment" },
  { headerName: "Invoice", field: "invoice_attachment" },
];

const defaultColDef = {
  resizable: true,
  sortable: false,
  cellStyle: { textAlign: "left" },
  headerClass: "ag-left-aligned-header",
  maxWidth: 300,
  minWidth: 100,
};

const STATUS_COLORS = {
  Approved: "text-green-600 bg-green-50 border-green-200",
  Returned: "text-red-600 bg-red-50 border-red-200",
  Rejected: "text-red-600 bg-red-50 border-red-200",
  Initiated: "text-blue-600 bg-blue-50 border-blue-200",
};

function StatusBadge({ value }) {
  if (!value) return null;
  const colorClass = STATUS_COLORS[value] || "text-gray-600 bg-gray-50 border-gray-200";
  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${colorClass}`}
    >
      {value}
    </span>
  );
}

function buildFilterParams(filterModel) {
  if (!filterModel) return {};
  const params = {};
  const operatorMap = {
    contains: "icontains",
    equals: "",
    startsWith: "istartswith",
    endsWith: "iendswith",
    greaterThan: "gt",
    greaterThanOrEqual: "gte",
    lessThan: "lt",
    lessThanOrEqual: "lte",
  };

  for (const [field, model] of Object.entries(filterModel)) {
    const condition = model.condition1 || model;
    const filterType = condition.type;
    const value = condition.filter ?? condition.dateFrom ?? "";
    if (value === "" || value === null || value === undefined) continue;
    const operator = operatorMap[filterType];
    if (operator === undefined) continue;
    const key = operator ? `${field}.${operator}` : field;
    params[key] = String(value);
  }
  return params;
}

export default function RemittanceReportPage() {
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const queryClient = useQueryClient();
  const { navSelectedItem, setNavSelectedItem, findByPath } = useUiConfig();

  const [gridApi, setGridApi] = useState(null);
  const [activeTab, setActiveTab] = useState("all");
  const [searchTerm, setSearchTerm] = useState("");
  const [gridFilterModel, setGridFilterModel] = useState({});
  const [selectedRows, setSelectedRows] = useState([]);
  const [isDeleting, setIsDeleting] = useState(false);
  const [pageSize, setPageSize] = useState(DEFAULT_PAGE_SIZE);

  // Sync nav selection with proper deps (matching original ListView pattern)
  useEffect(() => {
    const matched = findByPath(pathname);
    if (matched && matched.url !== navSelectedItem?.url) {
      setNavSelectedItem(matched);
    }
  }, [pathname, findByPath, navSelectedItem, setNavSelectedItem]);

  const extraParams = useMemo(() => {
    const params = { ...buildFilterParams(gridFilterModel) };
    if (searchTerm) params.search = searchTerm;
    if (activeTab === "cancelled") {
      params.status = "Returned";
    }
    return params;
  }, [searchTerm, gridFilterModel, activeTab]);

  const prevParamsRef = useRef(extraParams);
  useEffect(() => {
    if (gridApi && prevParamsRef.current !== extraParams) {
      prevParamsRef.current = extraParams;
      gridApi.purgeInfiniteCache();
    }
  }, [extraParams, gridApi]);

  const onGridReady = useCallback((params) => {
    setGridApi(params.api);
  }, []);

  useGridDatasource(gridApi, navSelectedItem, extraParams);

  // Render file URL as clickable link (just the filename)
  const fileCellRenderer = useCallback((params) => {
    const value = params.value;
    if (!value) return null;
    const fileName = value.split("/").pop();
    return (
      <a
        href={`${import.meta.env.VITE_API_BASE_URL?.replace("/api", "") || "http://127.0.0.1:8000"}${value.startsWith("/") ? "" : "/media/"}${value}`}
        target="_blank"
        rel="noreferrer"
        className="text-xs font-medium text-primary underline underline-offset-2 hover:text-primary/80 truncate block max-w-[120px]"
        title={fileName}
      >
        {fileName}
      </a>
    );
  }, []);

  const columnDefs = useMemo(() => {
    const textCols = DEFAULT_COLUMNS.map((col) => {
      if (col.field === "status") {
        return {
          ...col,
          cellRenderer: (params) => <StatusBadge value={params.value} />,
        };
      }
      return col;
    });
    const fileCols = FILE_COLUMNS.map((col) => ({
      ...col,
      cellRenderer: fileCellRenderer,
      filter: false,
      sortable: false,
    }));
    return [...textCols, ...fileCols];
  }, [fileCellRenderer]);

  const handleFilterChanged = useCallback(() => {
    if (!gridApi) return;
    const model = gridApi.getFilterModel();
    setGridFilterModel(model || {});
  }, [gridApi]);

  const handlePaginationChanged = useCallback(() => {
    if (!gridApi) return;
    const newSize = gridApi.paginationGetPageSize();
    if (newSize && newSize !== pageSize) setPageSize(newSize);
  }, [gridApi, pageSize]);

  const handleSelectionChanged = useCallback(() => {
    if (!gridApi) return;
    setSelectedRows(gridApi.getSelectedRows());
  }, [gridApi]);

  const handleRefresh = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: [navSelectedItem?.title] });
    if (gridApi) gridApi.purgeInfiniteCache();
  }, [gridApi, navSelectedItem, queryClient]);

  const handleDownload = useCallback(() => {
    if (!navSelectedItem?.api_path) return;
    api
      .get(navSelectedItem.api_path + "/", { params: { download: true, ...extraParams } })
      .then((res) => {
        const blob = new Blob([res.data], { type: "text/csv" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `Remittance_Report_${activeTab === "cancelled" ? "Cancelled" : "All"}.csv`;
        a.click();
        URL.revokeObjectURL(url);
      });
  }, [navSelectedItem, extraParams, activeTab]);

  const handleDelete = useCallback(async () => {
    if (!selectedRows.length || !navSelectedItem?.api_path) return;
    const count = selectedRows.length;
    if (!window.confirm(`Are you sure you want to delete ${count} record${count > 1 ? "s" : ""}?`))
      return;
    setIsDeleting(true);
    try {
      await Promise.all(
        selectedRows.map((row) => api.delete(`${navSelectedItem.api_path}/${row.id}/`))
      );
      toast.success(`${count} record${count > 1 ? "s" : ""} deleted`);
      setSelectedRows([]);
      queryClient.invalidateQueries({ queryKey: [navSelectedItem.title] });
      if (gridApi) {
        gridApi.deselectAll();
        gridApi.purgeInfiniteCache();
      }
    } catch (err) {
      toast.error(`Delete failed: ${err.response?.data?.message || err.message}`);
    } finally {
      setIsDeleting(false);
    }
  }, [selectedRows, navSelectedItem, gridApi, queryClient]);

  // Double-click opens the full workflow form inline in the remittance report
  const handleRowDoubleClick = useCallback(
    (event) => {
      const remittanceId = event.data?.id;
      if (remittanceId != null) {
        navigate(`/remittance-report/${remittanceId}/edit`);
      } else {
        toast.error("Invalid record.");
      }
    },
    [navigate]
  );

  const handleTabChange = useCallback(
    (value) => {
      setActiveTab(value);
      setSearchTerm("");
      setGridFilterModel({});
      setSelectedRows([]);
    },
    []
  );

  const canDelete = useMemo(() => {
    const perms = navSelectedItem?.permissions || [];
    const modelName = (navSelectedItem?.title || "").toLowerCase().replace(/\s+/g, "");
    return perms.includes(`delete_${modelName}`);
  }, [navSelectedItem]);

  return (
    <div className="p-4">
      <p className="text-left text-xl font-bold pb-3">&nbsp;Remittance Report</p>

      {/* Filter buttons */}
      <Card className="mb-4 p-1">
        <div className="flex items-center gap-2 p-1">
          <Button
            variant={activeTab === "all" ? "default" : "outline"}
            size="sm"
            onClick={() => handleTabChange("all")}
            className="text-sm font-medium"
          >
            Remittance Report
          </Button>
          <Button
            variant={activeTab === "cancelled" ? "destructive" : "outline"}
            size="sm"
            onClick={() => handleTabChange("cancelled")}
            className="text-sm font-medium"
          >
            Cancelled Requests
          </Button>
        </div>
      </Card>

      <ListViewHeader
        onRefresh={handleRefresh}
        onDownload={handleDownload}
        onSearch={setSearchTerm}
        onDelete={canDelete ? handleDelete : undefined}
        deleteDisabled={selectedRows.length === 0 || isDeleting}
        selectedCount={selectedRows.length}
      />

      <br />

      <div className="aggrid">
        <AgGridReact
          key={activeTab}
          defaultColDef={defaultColDef}
          columnDefs={columnDefs}
          pagination={true}
          autoSizeStrategy={{ type: "fitGridWidth" }}
          theme={gridTheme}
          rowModelType="infinite"
          paginationPageSize={pageSize}
          paginationPageSizeSelector={[10, 20, 50, 100]}
          cacheBlockSize={pageSize}
          onGridReady={onGridReady}
          onRowDoubleClicked={handleRowDoubleClick}
          onFilterChanged={handleFilterChanged}
          onPaginationChanged={handlePaginationChanged}
          rowSelection="multiple"
          onSelectionChanged={handleSelectionChanged}
          getRowId={(params) => String(params.data?.id)}
          suppressRowClickSelection={true}
        />
      </div>
    </div>
  );
}

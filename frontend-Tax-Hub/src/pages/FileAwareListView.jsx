import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { AgGridReact } from "ag-grid-react";
import { toast } from "sonner";

import { api, useGridDatasource, ListViewHeader, gridTheme } from "iron-stack-ui";
import { useUiConfig } from "@/utils/use-ui-config.js";

import { Spinner } from "@/components/ui/spinner.tsx";
import { downloadFileWithDialog } from "../utils/download-utils";

const DEFAULT_PAGE_SIZE = 20;

function getMediaUrl(value) {
  if (!value) return "";
  if (value.startsWith("http://") || value.startsWith("https://")) return value;
  const base = (import.meta.env.VITE_API_BASE_URL || "").replace("/api", "") || "http://127.0.0.1:8000";
  return `${base}${value.startsWith("/") ? "" : "/media/"}${value}`;
}

function getColumnFilter(fieldType) {
  switch (fieldType) {
    case "integer":
    case "float":
    case "decimal":
      return "agNumberColumnFilter";
    case "date":
    case "datetime":
      return "agDateColumnFilter";
    case "boolean":
      return false;
    default:
      return "agTextColumnFilter";
  }
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
    if (filterType === "inRange") {
      const from = condition.filter ?? condition.dateFrom;
      const to = condition.filterTo ?? condition.dateTo;
      if (from) params[`${field}.gte`] = from;
      if (to) params[`${field}.lte`] = to;
      continue;
    }
    const value = condition.filter ?? condition.dateFrom ?? "";
    if (!value) continue;
    const operator = operatorMap[filterType];
    if (operator === undefined) continue;
    const key = operator ? `${field}.${operator}` : field;
    params[key] = String(value);
  }
  return params;
}

const defaultColDef = {
  resizable: true,
  sortable: false,
  cellStyle: { textAlign: "left" },
  headerClass: "ag-left-aligned-header",
  maxWidth: 300,
  minWidth: 100,
};

export default function FileAwareListView() {
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const queryClient = useQueryClient();
  const { navSelectedItem, setNavSelectedItem, findByPath } = useUiConfig();

  const [gridApi, setGridApi] = useState(null);
  const [selectedRows, setSelectedRows] = useState([]);
  const [isDeleting, setIsDeleting] = useState(false);
  const [pageSize, setPageSize] = useState(DEFAULT_PAGE_SIZE);
  const [searchTerm, setSearchTerm] = useState("");
  const [gridFilterModel, setGridFilterModel] = useState({});
  const [downloadingUrl, setDownloadingUrl] = useState(null);

  useEffect(() => {
    const matched = findByPath(pathname);
    if (matched && matched.url !== navSelectedItem?.url) {
      setNavSelectedItem(matched);
    }
  }, [pathname, findByPath, navSelectedItem, setNavSelectedItem]);

  const metadataQuery = useQuery({
    queryKey: [navSelectedItem?.title, "metadata"],
    queryFn: () => api.options(navSelectedItem.api_path + "/"),
    enabled: Boolean(navSelectedItem?.api_path),
  });

  const postMetadata = metadataQuery.data?.data?.actions?.POST;
  const listFields = metadataQuery.data?.data?.list_display_fields;
  const filterFields = metadataQuery.data?.data?.filter_fields || [];

  const columns = useMemo(() => {
    if (!postMetadata || !Array.isArray(listFields)) return [];
    return listFields
      .map((key) => {
        if (key.includes(".")) {
          const parts = key.split(".");
          const label = parts.map((p) => p.charAt(0).toUpperCase() + p.slice(1)).join(" ");
          const isFilterable = filterFields.includes(key);
          return {
            headerName: label,
            field: key,
            valueGetter: (p) => p.data?.[key],
            filter: isFilterable ? "agTextColumnFilter" : false,
          };
        }
        const meta = postMetadata[key];
        if (!meta || meta.read_only) return null;
        const colDef = {
          headerName: meta.label,
          field: key,
          filter: filterFields.includes(key) ? getColumnFilter(meta.type) : false,
        };
        // Render file-type fields as clickable download links
        // DRF returns type "file upload" for FileField, so use includes()
        if (meta.type && meta.type.includes("file")) {
          colDef.cellRenderer = (params) => {
            const value = params.value;
            if (!value) return null;
            const fileName = value.split("/").pop();
            const url = getMediaUrl(value);
            const isDownloading = downloadingUrl === url;
            return (
              <span
                onClick={async (e) => {
                  e.stopPropagation();
                  if (isDownloading) return;
                  setDownloadingUrl(url);
                  try {
                    await downloadFileWithDialog(url, { suggestedName: fileName });
                  } catch (err) {
                    if (err.name !== "AbortError") {
                      console.error("Download failed:", err);
                    }
                  } finally {
                    setDownloadingUrl((prev) => (prev === url ? null : prev));
                  }
                }}
                className="text-xs font-medium text-primary underline underline-offset-2 hover:text-primary/80 truncate block max-w-[120px] cursor-pointer inline-flex items-center gap-1"
                title={fileName}
              >
                {isDownloading ? (
                  <>
                    <Spinner className="h-3 w-3" />
                    Downloading...
                  </>
                ) : (
                  fileName
                )}
              </span>
            );
          };
          colDef.filter = false;
          colDef.sortable = false;
        }
        return colDef;
      })
      .filter(Boolean);
  }, [postMetadata, listFields, filterFields, downloadingUrl]);

  const extraParams = useMemo(() => {
    const params = { ...buildFilterParams(gridFilterModel) };
    if (searchTerm) params.search = searchTerm;
    return params;
  }, [searchTerm, gridFilterModel]);

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

  const handleFilterChanged = useCallback(() => {
    if (!gridApi) return;
    setGridFilterModel(gridApi.getFilterModel() || {});
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
    api.get(navSelectedItem.api_path + "/", { params: { download: true, ...extraParams } })
      .then((res) => {
        const blob = new Blob([res.data], { type: "text/csv" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `${navSelectedItem.title}.csv`;
        a.click();
        URL.revokeObjectURL(url);
      });
  }, [navSelectedItem, extraParams]);

  const handleDelete = useCallback(async () => {
    if (!selectedRows.length || !navSelectedItem?.api_path) return;
    const count = selectedRows.length;
    if (!window.confirm(`Are you sure you want to delete ${count} record${count > 1 ? "s" : ""}?`)) return;
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

  const handleAdd = useCallback(() => {
    navigate(`/${navSelectedItem.url}/create`);
  }, [navigate, navSelectedItem]);

  const handleRowDoubleClick = useCallback((event) => {
    const perms = navSelectedItem?.permissions || [];
    const modelName = (navSelectedItem?.title || "").toLowerCase().replace(/\s+/g, "");
    const canEdit = perms.includes(`change_${modelName}`);
    if (!canEdit) return;
    const id = event.data?.id;
    if (id != null) {
      navigate(`/${navSelectedItem.url}/${id}/edit`);
    }
  }, [navigate, navSelectedItem]);

  const canAdd = useMemo(() => {
    const perms = navSelectedItem?.permissions || [];
    const modelName = (navSelectedItem?.title || "").toLowerCase().replace(/\s+/g, "");
    return perms.includes(`add_${modelName}`);
  }, [navSelectedItem]);

  const canDelete = useMemo(() => {
    const perms = navSelectedItem?.permissions || [];
    const modelName = (navSelectedItem?.title || "").toLowerCase().replace(/\s+/g, "");
    return perms.includes(`delete_${modelName}`);
  }, [navSelectedItem]);

  const selectionColumnDef = useMemo(() => {
    if (!canDelete) return null;
    return {
      headerCheckboxSelection: true,
      checkboxSelection: true,
      width: 50,
      maxWidth: 50,
      suppressHeaderMenuButton: true,
      filter: false,
      resizable: false,
      sortable: false,
    };
  }, [canDelete]);

  const allColumns = useMemo(() => {
    if (selectionColumnDef) return [selectionColumnDef, ...columns];
    return columns;
  }, [selectionColumnDef, columns]);

  if (!navSelectedItem) {
    return <div className="p-4 text-sm text-muted-foreground">Loading…</div>;
  }

  return (
    <div className="p-4">
      <p className="text-left text-xl font-bold pb-3">&nbsp;{navSelectedItem.title}</p>
      <ListViewHeader
        onAdd={canAdd ? handleAdd : undefined}
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
          defaultColDef={defaultColDef}
          columnDefs={allColumns}
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

import React, { useState, useMemo } from 'react';
import './EquipmentTable.css';

const EquipmentTable = ({ data, title = 'Equipment Data', showPagination = true }) => {
  const [currentPage, setCurrentPage] = useState(1);
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'ascending' });
  const [searchTerm, setSearchTerm] = useState('');
  
  const itemsPerPage = 10;

  // Safely handle data
  const tableData = useMemo(() => {
    if (!data) {
      return [];
    }
    
    // Handle both array and object with preview_rows
    if (Array.isArray(data)) {
      return data.length > 0 ? data : [];
    }
    
    // If data is object, check for preview_rows
    if (data.preview_rows && Array.isArray(data.preview_rows)) {
      return data.preview_rows;
    }
    
    return [];
  }, [data]);

  // Filter data based on search term
  const filteredData = useMemo(() => {
    if (!searchTerm) return tableData;
    
    return tableData.filter(item => 
      Object.values(item).some(value => 
        value?.toString().toLowerCase().includes(searchTerm.toLowerCase())
      )
    );
  }, [tableData, searchTerm]);

  // Sort data
  const sortedData = useMemo(() => {
    if (!sortConfig.key) return filteredData;

    return [...filteredData].sort((a, b) => {
      if (a[sortConfig.key] === null || a[sortConfig.key] === undefined) return 1;
      if (b[sortConfig.key] === null || b[sortConfig.key] === undefined) return -1;
      
      if (a[sortConfig.key] < b[sortConfig.key]) {
        return sortConfig.direction === 'ascending' ? -1 : 1;
      }
      if (a[sortConfig.key] > b[sortConfig.key]) {
        return sortConfig.direction === 'ascending' ? 1 : -1;
      }
      return 0;
    });
  }, [filteredData, sortConfig]);

  // Pagination
  const paginatedData = useMemo(() => {
    if (!showPagination) return sortedData;
    
    const startIndex = (currentPage - 1) * itemsPerPage;
    return sortedData.slice(startIndex, startIndex + itemsPerPage);
  }, [sortedData, currentPage, showPagination]);

  const totalPages = Math.ceil(sortedData.length / itemsPerPage);

  const handleSort = (key) => {
    let direction = 'ascending';
    if (sortConfig.key === key && sortConfig.direction === 'ascending') {
      direction = 'descending';
    }
    setSortConfig({ key, direction });
  };

  const getSortIcon = (columnKey) => {
    if (sortConfig.key !== columnKey) return '↕️';
    return sortConfig.direction === 'ascending' ? '↑' : '↓';
  };

  const renderCell = (value, key) => {
    if (value === null || value === undefined) return '-';
    
    // Format numeric values
    if (typeof value === 'number') {
      if (key.includes('flowrate')) return value.toFixed(2);
      if (key.includes('pressure')) return value.toFixed(2);
      if (key.includes('temperature')) return value.toFixed(1);
      return value.toString();
    }
    
    return value.toString();
  };

  if (tableData.length === 0) {
    return (
      <div className="equipment-table">
        <div className="table-header">
          <h2>{title}</h2>
        </div>
        <div className="table-empty-state">
          <div className="empty-icon">📋</div>
          <h3>No Equipment Data Available</h3>
          <p>Upload a CSV file to see equipment data here</p>
        </div>
      </div>
    );
  }

  const columns = Object.keys(tableData[0]);

  return (
    <div className="equipment-table">
      <div className="table-header">
        <h2>{title}</h2>
        <div className="table-controls">
          <div className="search-box">
            <input
              type="text"
              placeholder="🔍 Search equipment..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
          </div>
          <div className="table-info">
            <span className="record-count">
              {sortedData.length} records
              {searchTerm && ` (filtered)`}
            </span>
          </div>
        </div>
      </div>

      <div className="table-container">
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                {columns.map((column) => (
                  <th
                    key={column}
                    onClick={() => handleSort(column)}
                    className={sortConfig.key === column ? 'sorted' : ''}
                  >
                    <div className="th-content">
                      <span className="column-name">
                        {column.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </span>
                      <span className="sort-icon">{getSortIcon(column)}</span>
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {paginatedData.map((row, index) => (
                <tr key={index} className="table-row">
                  {columns.map((column) => (
                    <td key={column}>
                      {renderCell(row[column], column)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {showPagination && totalPages > 1 && (
        <div className="pagination">
          <button
            className="pagination-btn"
            onClick={() => setCurrentPage(1)}
            disabled={currentPage === 1}
          >
            ⏮️ First
          </button>
          <button
            className="pagination-btn"
            onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
            disabled={currentPage === 1}
          >
            ⬅️ Previous
          </button>
          
          <div className="page-numbers">
            {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
              let pageNum;
              if (totalPages <= 5) {
                pageNum = i + 1;
              } else if (currentPage <= 3) {
                pageNum = i + 1;
              } else if (currentPage >= totalPages - 2) {
                pageNum = totalPages - 4 + i;
              } else {
                pageNum = currentPage - 2 + i;
              }
              
              return (
                <button
                  key={pageNum}
                  className={`page-number ${currentPage === pageNum ? 'active' : ''}`}
                  onClick={() => setCurrentPage(pageNum)}
                >
                  {pageNum}
                </button>
              );
            })}
          </div>
          
          <button
            className="pagination-btn"
            onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
            disabled={currentPage === totalPages}
          >
            Next ➡️
          </button>
          <button
            className="pagination-btn"
            onClick={() => setCurrentPage(totalPages)}
            disabled={currentPage === totalPages}
          >
            Last ⏭️
          </button>
        </div>
      )}
    </div>
  );
};

export default EquipmentTable;

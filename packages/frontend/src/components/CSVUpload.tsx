/**
 * CSV Upload Component
 * Drag-and-drop file upload with validation
 */

import React, { useState, useCallback } from 'react';
import { uploadSalesData } from '../services/api';

interface CSVUploadProps {
  onUploadSuccess: (data: any) => void;
  onUploadError: (error: string) => void;
}

const CSVUpload: React.FC<CSVUploadProps> = ({ onUploadSuccess, onUploadError }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      const file = files[0];
      if (file.type === 'text/csv' || file.name.endsWith('.csv')) {
        setSelectedFile(file);
      } else {
        onUploadError('Please upload a CSV file');
      }
    }
  }, [onUploadError]);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      setSelectedFile(files[0]);
    }
  }, []);

  const handleUpload = async () => {
    if (!selectedFile) return;

    setIsUploading(true);
    const result = await uploadSalesData(selectedFile);
    setIsUploading(false);

    if (result.success) {
      onUploadSuccess(result.data);
      setSelectedFile(null);
    } else {
      onUploadError(result.error || 'Upload failed');
    }
  };

  return (
    <div style={{ width: '100%' }}>
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        style={{
          border: `2px dashed ${isDragging ? '#1a73e8' : '#ccc'}`,
          borderRadius: '8px',
          padding: '3rem',
          textAlign: 'center',
          backgroundColor: isDragging ? '#e8f0fe' : '#fafafa',
          cursor: 'pointer',
          transition: 'all 0.3s ease',
        }}
      >
        <input
          type="file"
          accept=".csv"
          onChange={handleFileSelect}
          style={{ display: 'none' }}
          id="csv-upload"
        />
        <label htmlFor="csv-upload" style={{ cursor: 'pointer' }}>
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📁</div>
          <p style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>
            {selectedFile ? selectedFile.name : 'Drag and drop your CSV file here'}
          </p>
          <p style={{ color: '#666', fontSize: '0.9rem' }}>
            or click to browse
          </p>
        </label>
      </div>

      {selectedFile && (
        <div style={{ marginTop: '1rem', textAlign: 'center' }}>
          <button
            onClick={handleUpload}
            disabled={isUploading}
            style={{
              padding: '0.75rem 2rem',
              backgroundColor: isUploading ? '#ccc' : '#1a73e8',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              fontSize: '1rem',
              cursor: isUploading ? 'not-allowed' : 'pointer',
            }}
          >
            {isUploading ? 'Uploading...' : 'Upload File'}
          </button>
        </div>
      )}

      <div style={{ marginTop: '1.5rem', padding: '1rem', backgroundColor: '#e8f5e9', borderRadius: '4px' }}>
        <p style={{ fontSize: '0.9rem', color: '#2e7d32', marginBottom: '0.5rem' }}>
          <strong>Required CSV columns:</strong>
        </p>
        <ul style={{ fontSize: '0.9rem', color: '#2e7d32', marginLeft: '1.5rem' }}>
          <li>date (YYYY-MM-DD format)</li>
          <li>sku (product identifier)</li>
          <li>quantity (units sold)</li>
          <li>category (optional)</li>
          <li>price (optional)</li>
        </ul>
      </div>
    </div>
  );
};

export default CSVUpload;

import { useState } from 'react';

const useReportGenerator = () => {
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);
  const [reportError, setReportError] = useState(null);

  const generateReport = async (publicId, title) => {
    try {
      setIsGeneratingReport(true);
      setReportError(null);
      
      const response = await fetch(`http://localhost:8000/api/surveys/${publicId}/report/`, {
        method: 'GET',
        headers: {
          'Accept': 'application/pdf'
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const blob = await response.blob();

      const url = window.URL.createObjectURL(blob);
     
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = `survey_report_${title.replace(/\s+/g, '_')}.pdf`;
   
      document.body.appendChild(a);
      a.click();
    
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      setIsGeneratingReport(false);
    } catch (error) {
      console.error('Error generating report:', error);
      setReportError(`Failed to generate report: ${error.message}`);
      setIsGeneratingReport(false);
    }
  };

  return {
    isGeneratingReport,
    reportError,
    generateReport,
    clearReportError: () => setReportError(null)
  };
};

export default useReportGenerator; 
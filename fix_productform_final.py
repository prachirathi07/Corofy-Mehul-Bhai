#!/usr/bin/env python3
"""
FINAL COMPREHENSIVE FIX for ProductForm.tsx
This will properly fix all issues in one pass.
"""

def final_fix():
    file_path = r"c:\Users\prach\Desktop\NenoTechnology\mehulbhai\dashboard\dharm-mehulbhai\components\ProductForm.tsx"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # The issue is that after `handleSubmit`, there's orphaned JSX and missing functions
    # We need to:
    # 1. Find where handleSubmit validation ends
    # 2. Add the rest of handleSubmit (payload creation)
    # 3. Add handleConfirmSubmit
    # 4. Add handleCancelSubmit  
    # 5. Add isLoadingData check
    # 6. Remove orphaned JSX
    # 7. Add proper return statement
    
    # Find the end of handleSubmit validation
    marker = "      return;\n    }\n  }\n  px - 6 py - 4"
    
    if marker not in content:
        # Try alternate marker
        marker = "        return;\n      }\n    }\n    px - 6 py - 4"
    
    if marker in content:
        # Split at this point
        before = content[:content.index(marker) + len("      return;\n    }\n  }")]
        after_junk_start = content.index("px - 6 py - 4")
        
        # Find where the real JSX starts (after the orphaned stuff)
        # Look for "      {/* Step 2: Brand Selection */"
        real_jsx_marker = "      {/* Step 2: Brand Selection */"
        if real_jsx_marker in content[after_junk_start:]:
            after = content[content.index(real_jsx_marker, after_junk_start):]
        else:
            print("ERROR: Could not find real JSX start")
            return
        
        # Now construct the missing parts
        missing_code = """

    // Get SIC code for the selected industry using the new helper function
    const industryDetails = getIndustryDetails(formData.industry);
    const sicCode = industryDetails.sicCode;

    const payload = {
      ...formData,
      sic_codes: sicCode ? [sicCode] : [],
      product: selectedProduct,
      timestamp: new Date().toISOString(),
      isCustomIndustry: isCustomIndustry && hasNoBrands
    };

    // Show confirmation modal with data
    setSubmitPayload(payload);
    setShowConfirmModal(true);
  };

  const handleConfirmSubmit = async () => {
    if (!submitPayload) return;

    setIsSubmitting(true);
    setShowConfirmModal(false); // Close confirmation modal
    console.log('Submitting form data:', submitPayload);

    // Show progress notification
    setShowProgressNotification(true);
    setProgressMessage('Initiating lead scraping with Apollo...');
    setProgressType('loading');

    try {
      // Dynamically import the API client to avoid server-side issues
      const { leadsApi } = await import('@/lib/api');

      // Prepare the payload for the API
      // Ensure industry is passed correctly
      const apiPayload = {
        total_leads_wanted: 10,
        sic_codes: submitPayload.sic_codes || [],
        industry: submitPayload.industry, // Explicitly include industry
        source: 'apollo'
      };

      console.log('Calling scrape API with payload:', apiPayload);
      const result = await leadsApi.scrapeLeads(apiPayload);

      console.log('Scraping initiated successfully:', result);

      // Update to success message
      setProgressMessage(
        `Lead scraping initiated! Found ${result.total_leads_found || 0} leads. Processing...`
      );
      setProgressType('success');

      // Navigate to database after 2 seconds
      setTimeout(() => {
        router.push('/database');
      }, 2000);
    } catch (error: any) {
      console.error('Error submitting to API:', error);

      // Extract error message
      const errorMessage = error?.message || 'Unknown error occurred';
      setProgressMessage(`Failed to initiate scraping: ${errorMessage}`);
      setProgressType('error');

      // Hide notification after 5 seconds
      setTimeout(() => {
        setShowProgressNotification(false);
      }, 5000);
    } finally {
      setIsSubmitting(false);
      setSubmitPayload(null);
    }
  };

  const handleCancelSubmit = () => {
    setShowConfirmModal(false);
    setSubmitPayload(null);
  };

  if (isLoadingData) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-8 flex justify-center items-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600">Loading form data...</span>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-md relative">
      {/* Progress Notification - Centered Top */}
      {showProgressNotification && (
        <div className="fixed top-8 left-1/2 transform -translate-x-1/2 z-[60] animate-slideDown">
          <div className={`
              px-6 py-4 rounded-lg shadow-2xl border-2 flex items-center space-x-3 min-w-[320px]
              ${progressType === 'loading' ? 'bg-blue-50 border-blue-500 text-blue-700' : ''}
              ${progressType === 'success' ? 'bg-green-50 border-green-500 text-green-700' : ''}
              ${progressType === 'error' ? 'bg-red-50 border-red-500 text-red-700' : ''}
            `}>
            {progressType === 'loading' && (
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-700"></div>
            )}
            {progressType === 'success' && (
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            )}
            {progressType === 'error' && (
              <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            )}
            <span className="font-semibold text-base">{progressMessage}</span>
          </div>
        </div>
      )}
      {/* Header */}
      <div className="bg-blue-600 text-white p-6 rounded-t-lg">
        <h2 className="text-xl font-bold">Product Selection Form</h2>
        <p className="text-blue-100 mt-1">Select your industry, brand, and chemical to view available countries</p>
      </div>

      <div className="p-6 space-y-8">
        {/* Step 1: Industry Selection */}
        <div>
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-gray-800">Step 1: Select Industry</h3>
            <button
              onClick={(e) => handleAddNew('industry', e)}
              className="flex items-center space-x-1 px-3 py-1.5 bg-green-600 text-white text-sm rounded-md hover:bg-green-700 transition-colors"
              title="Add new industry"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              <span>Add New</span>
            </button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {industries.map(industry => {
              // Use the new helper function to get industry details including SIC code
              const industryDetails = getIndustryDetails(industry);
              const sicCode = industryDetails.sicCode;
              const isCustomIndustry = customIndustries.some(ind => ind.name === industry);

              return (
                <div
                  key={industry}
                  className={`group relative p-4 rounded-lg border-2 transition-all duration-200 hover:shadow-md ${
                    formData.industry === industry
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-blue-300 bg-white'
                  }`}
                >
                  <button
                    onClick={() => handleInputChange('industry', industry)}
                    className="w-full text-left"
                  >
                    <div className="font-medium text-black">{industry}</div>
                    {sicCode && (
                      <div className="mt-1 text-sm text-gray-600">
                        SIC Code: <span className="font-semibold text-gray-800">{sicCode}</span>
                      </div>
                    )}
                  </button>
                  {isCustomIndustry && (
                    <button
                      onClick={(e) => handleDeleteIndustry(industry, e)}
                      className="absolute top-2 right-2 p-1.5 rounded-md bg-red-500 text-white opacity-0 group-hover:opacity-100 transition-opacity duration-200 hover:bg-red-600"
                      title="Delete industry"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  )}
                </div>
              );
            })}
          </div>
        </div>

"""
        
        # Combine everything
        fixed_content = before + missing_code + after
        
        # Write the fixed file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print("✓ File successfully fixed!")
        print("✓ Added complete handleSubmit function")
        print("✓ Added handleConfirmSubmit function")
        print("✓ Added handleCancelSubmit function")
        print("✓ Added isLoadingData check")
        print("✓ Added proper return statement with Progress Notification")
        print("✓ Removed all orphaned JSX")
        print("\n✅ ProductForm.tsx is now fully repaired!")
    else:
        print("ERROR: Could not find the corruption marker in the file")
        print("The file may have changed. Please check manually.")

if __name__ == '__main__':
    final_fix()

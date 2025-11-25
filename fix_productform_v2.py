#!/usr/bin/env python3
"""
Comprehensive fix for ProductForm.tsx
This script will:
1. Remove ALL orphaned JSX after handleSubmit
2. Add the missing handleConfirmSubmit and handleCancelSubmit functions
3. Add the proper isLoadingData check
4. Ensure the return statement is properly placed
"""

def fix_productform_comprehensive():
    file_path = r"c:\Users\prach\Desktop\NenoTechnology\mehulbhai\dashboard\dharm-mehulbhai\components\ProductForm.tsx"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find where handleSubmit ends (after the last closing brace of the validation)
    # It should end after: "    }\n"  following the "return;" for validation
    
    # Split into lines for easier manipulation
    lines = content.split('\n')
    
    fixed_lines = []
    i = 0
    skip_mode = False
    found_handlesubmit_end = False
    
    while i < len(lines):
        line = lines[i]
        
        # Detect the end of handleSubmit (after validation checks)
        if not found_handlesubmit_end and 'const handleSubmit = (e: React.FormEvent) =>' in line:
            # We're in handleSubmit
            fixed_lines.append(line)
            i += 1
            
            # Copy until we find the end of validation (the last "}")
            depth = 0
            validation_complete = False
            
            while i < len(lines):
                line = lines[i]
                fixed_lines.append(line)
                
                # Track the validation section
                if 'if (!formData.brandName || !formData.chemicalName)' in line:
                    validation_complete = True
                
                if validation_complete and line.strip() == '}':
                    # This is likely the end of the if block for validation
                    # Now add the missing code
                    i += 1
                    
                    # Add the rest of handleSubmit
                    fixed_lines.append('')
                    fixed_lines.append('    // Get SIC code for the selected industry using the new helper function')
                    fixed_lines.append('    const industryDetails = getIndustryDetails(formData.industry);')
                    fixed_lines.append('    const sicCode = industryDetails.sicCode;')
                    fixed_lines.append('')
                    fixed_lines.append('    const payload = {')
                    fixed_lines.append('      ...formData,')
                    fixed_lines.append('      sic_codes: sicCode ? [sicCode] : [],')
                    fixed_lines.append('      product: selectedProduct,')
                    fixed_lines.append('      timestamp: new Date().toISOString(),')
                    fixed_lines.append('      isCustomIndustry: isCustomIndustry && hasNoBrands')
                    fixed_lines.append('    };')
                    fixed_lines.append('')
                    fixed_lines.append('    // Show confirmation modal with data')
                    fixed_lines.append('    setSubmitPayload(payload);')
                    fixed_lines.append('    setShowConfirmModal(true);')
                    fixed_lines.append('  };')
                    fixed_lines.append('')
                    
                    # Add handleConfirmSubmit
                    fixed_lines.append('  const handleConfirmSubmit = async () => {')
                    fixed_lines.append('    if (!submitPayload) return;')
                    fixed_lines.append('')
                    fixed_lines.append('    setIsSubmitting(true);')
                    fixed_lines.append('    setShowConfirmModal(false); // Close confirmation modal')
                    fixed_lines.append('    console.log(\'Submitting form data:\', submitPayload);')
                    fixed_lines.append('')
                    fixed_lines.append('    // Show progress notification')
                    fixed_lines.append('    setShowProgressNotification(true);')
                    fixed_lines.append('    setProgressMessage(\'Initiating lead scraping with Apollo...\');')
                    fixed_lines.append('    setProgressType(\'loading\');')
                    fixed_lines.append('')
                    fixed_lines.append('    try {')
                    fixed_lines.append('      // Dynamically import the API client to avoid server-side issues')
                    fixed_lines.append('      const { leadsApi } = await import(\'@/lib/api\');')
                    fixed_lines.append('')
                    fixed_lines.append('      // Prepare the payload for the API')
                    fixed_lines.append('      // Ensure industry is passed correctly')
                    fixed_lines.append('      const apiPayload = {')
                    fixed_lines.append('        total_leads_wanted: 10,')
                    fixed_lines.append('        sic_codes: submitPayload.sic_codes || [],')
                    fixed_lines.append('        industry: submitPayload.industry, // Explicitly include industry')
                    fixed_lines.append('        source: \'apollo\'')
                    fixed_lines.append('      };')
                    fixed_lines.append('')
                    fixed_lines.append('      console.log(\'Calling scrape API with payload:\', apiPayload);')
                    fixed_lines.append('      const result = await leadsApi.scrapeLeads(apiPayload);')
                    fixed_lines.append('')
                    fixed_lines.append('      console.log(\'Scraping initiated successfully:\', result);')
                    fixed_lines.append('')
                    fixed_lines.append('      // Update to success message')
                    fixed_lines.append('      setProgressMessage(')
                    fixed_lines.append('        `Lead scraping initiated! Found ${result.total_leads_found || 0} leads. Processing...`')
                    fixed_lines.append('      );')
                    fixed_lines.append('      setProgressType(\'success\');')
                    fixed_lines.append('')
                    fixed_lines.append('      // Navigate to database after 2 seconds')
                    fixed_lines.append('      setTimeout(() => {')
                    fixed_lines.append('        router.push(\'/database\');')
                    fixed_lines.append('      }, 2000);')
                    fixed_lines.append('    } catch (error: any) {')
                    fixed_lines.append('      console.error(\'Error submitting to API:\', error);')
                    fixed_lines.append('')
                    fixed_lines.append('      // Extract error message')
                    fixed_lines.append('      const errorMessage = error?.message || \'Unknown error occurred\';')
                    fixed_lines.append('      setProgressMessage(`Failed to initiate scraping: ${errorMessage}`);')
                    fixed_lines.append('      setProgressType(\'error\');')
                    fixed_lines.append('')
                    fixed_lines.append('      // Hide notification after 5 seconds')
                    fixed_lines.append('      setTimeout(() => {')
                    fixed_lines.append('        setShowProgressNotification(false);')
                    fixed_lines.append('      }, 5000);')
                    fixed_lines.append('    } finally {')
                    fixed_lines.append('      setIsSubmitting(false);')
                    fixed_lines.append('      setSubmitPayload(null);')
                    fixed_lines.append('    }')
                    fixed_lines.append('  };')
                    fixed_lines.append('')
                    
                    # Add handleCancelSubmit
                    fixed_lines.append('  const handleCancelSubmit = () => {')
                    fixed_lines.append('    setShowConfirmModal(false);')
                    fixed_lines.append('    setSubmitPayload(null);')
                    fixed_lines.append('  };')
                    fixed_lines.append('')
                    
                    # Add isLoadingData check
                    fixed_lines.append('  if (isLoadingData) {')
                    fixed_lines.append('    return (')
                    fixed_lines.append('      <div className="bg-white rounded-lg shadow-lg p-8 flex justify-center items-center">')
                    fixed_lines.append('        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>')
                    fixed_lines.append('        <span className="ml-2 text-gray-600">Loading form data...</span>')
                    fixed_lines.append('      </div>')
                    fixed_lines.append('    );')
                    fixed_lines.append('  }')
                    fixed_lines.append('')
                    
                    found_handlesubmit_end = True
                    skip_mode = True  # Skip all the orphaned JSX
                    break
                
                i += 1
            continue
        
        # Skip orphaned JSX until we find the proper return statement
        if skip_mode:
            # Look for the start of the main return with Progress Notification
            if 'return (' in line and i > 800:
                # Found the proper return, stop skipping
                skip_mode = False
                fixed_lines.append(line)
                i += 1
                continue
            else:
                # Still in skip mode, don't add this line
                i += 1
                continue
        
        fixed_lines.append(line)
        i += 1
    
    # Write the fixed content
    fixed_content = '\n'.join(fixed_lines)
    with open(file_path, 'w', encoding='utf-8', newline='\r\n') as f:
        f.write(fixed_content)
    
    print(f"✓ Fixed file written with {len(fixed_lines)} lines (original had {len(lines)} lines)")
    print("✓ Added handleConfirmSubmit function")
    print("✓ Added handleCancelSubmit function")
    print("✓ Added isLoadingData check")
    print("✓ Removed orphaned JSX")
    print("\n✓ File repair complete!")

if __name__ == '__main__':
    fix_productform_comprehensive()

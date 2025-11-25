#!/usr/bin/env python3
"""
Script to fix the corrupted ProductForm.tsx file.
This removes orphaned JSX and adds missing functions.
"""

import re

def fix_productform():
    file_path = r"c:\Users\prach\Desktop\NenoTechnology\mehulbhai\dashboard\dharm-mehulbhai\components\ProductForm.tsx"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find the corruption points
    fixed_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Skip the orphaned JSX block (lines ~835-900)
        # This is the "px - 6 py - 4..." garbage
        if 'px - 6 py - 4 rounded - lg shadow' in line:
            print(f"Found orphaned JSX at line {i+1}, skipping corruption block...")
            # Skip until we find the next proper function or closing
            while i < len(lines):
                if lines[i].strip().startswith('const handleSubmit') or \
                   lines[i].strip().startswith('const handle') or \
                   lines[i].strip().startswith('if (isLoadingData)') or \
                   lines[i].strip().startswith('return ('):
                    break
                i += 1
            continue
        
        # Fix the broken confirmDeleteIndustry - add missing closing
        if i > 0 and 'setDeleteModal({ isOpen: false, type: null, itemName' in line and \
           'confirmDeleteIndustry' in ''.join(lines[max(0, i-50):i]):
            fixed_lines.append(line)
            # Check if we need to add closing brace for confirmDeleteIndustry
            if i + 1 < len(lines) and not lines[i+1].strip().startswith('}'):
                fixed_lines.append('  };\n')
                fixed_lines.append('\n')
                fixed_lines.append('  // Handle deleting custom brand\n')
                fixed_lines.append('  const handleDeleteBrand = async (brandName: string, e: React.MouseEvent) => {\n')
                fixed_lines.append('    e.stopPropagation();\n')
                fixed_lines.append('\n')
                fixed_lines.append('    // Show delete confirmation modal\n')
                fixed_lines.append('    setDeleteModal({\n')
                fixed_lines.append('      isOpen: true,\n')
                fixed_lines.append('      type: \'brand\',\n')
                fixed_lines.append('      itemName: brandName,\n')
                fixed_lines.append('      onConfirm: () => confirmDeleteBrand(brandName)\n')
                fixed_lines.append('    });\n')
                fixed_lines.append('  };\n')
                fixed_lines.append('\n')
                fixed_lines.append('  const confirmDeleteBrand = async (brandName: string) => {\n')
                fixed_lines.append('\n')
                fixed_lines.append('    try {\n')
                fixed_lines.append('      if (!formData.industry) return;\n')
                fixed_lines.append('\n')
                fixed_lines.append('      const industry = formData.industry;\n')
                fixed_lines.append('      const customData: CustomFormData = {\n')
                fixed_lines.append('        industries: [...customIndustries],\n')
                fixed_lines.append('        brands: { ...customBrands },\n')
                fixed_lines.append('        chemicals: { ...customChemicals },\n')
                fixed_lines.append('        selectedCountries: [...customSelectedCountries],\n')
                fixed_lines.append('        lastUpdated: new Date().toISOString()\n')
                fixed_lines.append('      };\n')
                fixed_lines.append('\n')
                fixed_lines.append('      // Remove brand from customBrands\n')
                fixed_lines.append('      if (customData.brands[industry]) {\n')
                fixed_lines.append('        customData.brands[industry] = customData.brands[industry].filter(b => b !== brandName);\n')
                fixed_lines.append('        if (customData.brands[industry].length === 0) {\n')
                fixed_lines.append('          delete customData.brands[industry];\n')
                fixed_lines.append('        }\n')
                fixed_lines.append('      }\n')
                fixed_lines.append('\n')
                fixed_lines.append('      // Remove associated chemicals\n')
                fixed_lines.append('      const key = `${industry}::${brandName}`;\n')
                fixed_lines.append('      if (customData.chemicals[key]) {\n')
                fixed_lines.append('        delete customData.chemicals[key];\n')
                fixed_lines.append('      }\n')
                fixed_lines.append('\n')
                fixed_lines.append('      // Save to API\n')
                fixed_lines.append('      const success = await saveCustomData(customData);\n')
                fixed_lines.append('\n')
                fixed_lines.append('      if (success) {\n')
                fixed_lines.append('        // Update local state\n')
                fixed_lines.append('        setCustomBrands(customData.brands);\n')
                fixed_lines.append('        setCustomChemicals(customData.chemicals);\n')
                fixed_lines.append('\n')
                fixed_lines.append('        // Clear formData if deleted brand was selected\n')
                fixed_lines.append('        if (formData.brandName === brandName) {\n')
                fixed_lines.append('          setFormData(prev => ({\n')
                fixed_lines.append('            ...prev,\n')
                fixed_lines.append('            brandName: \'\',\n')
                fixed_lines.append('            chemicalName: \'\',\n')
                fixed_lines.append('            countries: []\n')
                fixed_lines.append('          }));\n')
                fixed_lines.append('        }\n')
                fixed_lines.append('\n')
                fixed_lines.append('        setSubmitMessage(\'Brand deleted successfully!\');\n')
                fixed_lines.append('        setTimeout(() => {\n')
                fixed_lines.append('          setSubmitMessage(\'\');\n')
                fixed_lines.append('        }, 3000);\n')
                fixed_lines.append('      } else {\n')
                fixed_lines.append('        showError(\'Delete Error\', \'Failed to delete brand. Please try again.\');\n')
                fixed_lines.append('      }\n')
                fixed_lines.append('    } catch (error) {\n')
                fixed_lines.append('      console.error(\'Error deleting brand:\', error);\n')
                fixed_lines.append('      showError(\'Delete Error\', \'Failed to delete brand. Please try again.\');\n')
                fixed_lines.append('    }\n')
                fixed_lines.append('    setDeleteModal({ isOpen: false, type: null, itemName: \'\', onConfirm: null });\n')
                fixed_lines.append('  };\n')
                print(f"Added missing handleDeleteBrand functions after line {i+1}")
            i += 1
            continue
        
        # Skip duplicate/broken handleDeleteBrand/Chemical definitions
        if ('// Handle deleting custom brand' in line or \
            'const handleDeleteBrand' in line or \
            '// Handle deleting custom chemical' in line or \
            'const handleDeleteChemical' in line or \
            'const confirmDeleteBrand' in line or \
            'const confirmDeleteChemical' in line) and i > 700 and i < 900:
            # Skip this broken section
            print(f"Skipping broken delete function at line {i+1}")
            i += 1
            continue
            
        fixed_lines.append(line)
        i += 1
    
    # Write the fixed content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print(f"Fixed file written with {len(fixed_lines)} lines (original had {len(lines)} lines)")
    print("File repair complete!")

if __name__ == '__main__':
    fix_productform()

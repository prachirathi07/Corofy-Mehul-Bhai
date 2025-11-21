"""
Email templates and product catalogs for Corofy email automation.
Extracted from n8n workflow.
"""

PRODUCT_CATALOGS = {
    "Lubricant": [
        "Monoethylene Glycol",
        "Diethylene Glycol",
        "Urea Solution / Diesel Exhaust Fluid / AdBlue",
        "Total Base Number Improver Calcium based",
        "Zinc Booster",
        "Dispersant / Polyisobutylene Succinimide / PIBSI",
        "Additive Packages for Petro and Diesel Engine",
        "Pour Point Depressant",
        "Brake Fluid DOT 3 & DOT 4"
    ],
    "Oil & Gas": [
        "Cloud Point Glycol for Drilling",
        "Nonionic Polyalkylimide Glycol Blend",
        "Nonionic foaming agent",
        "Drilling Detergent",
        "Monoethylene Glycol",
        "Triethylene Glycol",
        "PAC - Polyanionic Cellulose",
        "Carboxymethyl Cellulose / CMC",
        "XC Polymer Xanthan Gum based",
        "Mono Ethanol Amine",
        "Sulfonated Asphalt",
        "Calcium Bromide Liquid 52%",
        "Primary & Secondary Emulsifier",
        "Corrosion Inhibitor Imidazoline Based",
        "Demulsifier Concentrate",
        "Pour Point Depressant",
        "Defoamers- Glycol, Silicone and Ethoxylate based",
        "Organophilic Clay",
        "N Methyl Aniline",
        "Methyl Diethylene Glycol",
        "Mud Thinner",
        "Mud Wetting Agent"
    ],
    "Agrochemical": [
        "Calcium Alkylbenzene Sulfonate / CaDDBS",
        "Nonylphenol Ethoxylate",
        "Castor Oil Ethoxylate",
        "Styrenated Phenol Ethoxylate / Tristyrylphenol Ethoxylate",
        "Blended Emulsifier Pair for EC",
        "Precipitated Silica",
        "Dispersing Agent for SC",
        "Wetting Agent for SC",
        "Dispersing Agent for WP & WDG",
        "Wetting Agent for WP & WDG",
        "Silicone Based Antifoam or Defoamer",
        "Strong Adjuvant",
        "Sulfur Wettable Dry Granules",
        "Chelated Metals as Microneutrients"
    ]
}

# HTML Templates with placeholders
# {{LeadName}} - Recipient's name
# {{BodyContent}} - AI generated body (if needed, though n8n templates seem static/hybrid)

EMAIL_TEMPLATES = {
    "Agrochemical": """<!DOCTYPE html>
<html>
  <body style="font-family: Arial, sans-serif; font-size: 14px; color: #333; line-height: 1.6; margin: 0; padding: 0;">
    <p>Hi {{LeadName}},</p>
    <p>Greetings from <b>Corofy</b>!</p>
    <p>
      We are a passionate team of professionals specializing in Specialty Chemicals for Agro Crop Protection and Nutrition, proudly certified with ISO 9001:2015 by UKAS Management Systems. With facilities in the UAE and India, and ready stocks in both regions, we are strategically positioned to serve global markets. We also arrange direct shipments from UAE, India, and China ensuring flexibility and reliability.
    </p>
    <p>Key Agro Chemicals we offer include:</p>
    <ul style="margin:0; padding-left:18px;">
      <li>Calcium Alkylbenzene Sulfonate / CaDDBS</li>
      <li>Nonylphenol Ethoxylate</li>
      <li>Castor Oil Ethoxylate</li>
      <li>Styrenated Phenol Ethoxylate / Tristyrylphenol Ethoxylate</li>
      <li>Blended Emulsifier Pair for EC</li>
      <li>Precipitated Silica</li>
      <li>Dispersing Agent for SC</li>
      <li>Wetting Agent for SC</li>
      <li>Dispersing Agent for WP & WDG</li>
      <li>Wetting Agent for WP & WDG</li>
      <li>Silicone Based Antifoam or Defoamer</li>
      <li>Strong Adjuvant</li>
      <li>Sulfur Wettable Dry Granules</li>
      <li>Chelated Metals as Microneutrients</li>
    </ul>
    <p>
      We would be pleased to explore potential collaboration and supply opportunities with your esteemed organization. Kindly let us know the next steps to move forward.
    </p>
    <p>Looking forward to your response.</p>
    <p style="margin-top:20px;">
      Best Regards,<br><br>
      <strong>Mehul Parmar</strong><br>
      Director – Commercial & Technical<br>
      Cell Phone: <a href="tel:+971554306280" style="color:#0066cc; text-decoration:none;">+971 554306280</a>
    </p>
    <hr style="border:0; border-top:1px solid #ccc; margin:20px 0;">
    <table style="font-size:13px; color:#333; font-family:Arial, sans-serif;">
      <tr>
        <td style="padding-right:10px; vertical-align:top;">
          <img src="https://media.licdn.com/dms/image/v2/D4D0BAQG4B_2SfqHmHQ/company-logo_200_200/company-logo_200_200/0/1706868984894/corofy_llc_logo?e=1759363200&v=beta&t=IRuzQ2YcCU9pPdvTAn2h0L3aXKAFB_ZtJ2EFBMandGU" 
             alt="Corofy Logo" 
             style="height:50px; width:auto;" />
        </td>
        <td style="vertical-align:top;">
          <strong>Corofy LLC</strong><br>
          510 – Goldcrest Executive, Cluster C, JLT – Dubai – United Arab Emirates<br>
          Tel: <a href="tel:+97142715611" style="color:#0066cc; text-decoration:none;">+971 4 271 5611</a> | 
          <a href="http://www.corofychem.com" style="color:#0066cc; text-decoration:none;">www.corofychem.com</a><br>
          Email: <a href="mailto:mehul@corofychem.com" style="color:#0066cc; text-decoration:none;">mehul@corofychem.com</a><br>
          <span style="color:#777;">ISO 9001:2015 Certified from UKAS Management Systems</span>
        </td>
      </tr>
    </table>
  </body>
</html>""",

    "Oil & Gas": """<!DOCTYPE html>
<html>
  <body style="font-family: Arial, sans-serif; font-size: 14px; color: #333; line-height: 1.6; margin: 0; padding: 0;">
    <p>Hi {{LeadName}},</p>
    <p>Greetings from <b>Corofy</b>!</p>
    <p>
      We are a professional team dedicated to providing Specialty Chemicals for the Oil & Gas industry, certified with ISO 9001:2015 by UKAS Management Systems. With facilities in the UAE and India, and strategic stock points in both locations, we ensure reliable global supply. We also arrange direct shipments from UAE, India, and China for maximum flexibility.
    </p>
    <p>Key Oil & Gas Chemicals we offer include:</p>
    <ul style="margin:0; padding-left:18px;">
      <li>Cloud Point Glycol for Drilling</li>
      <li>Nonionic Polyalkylimide Glycol Blend</li>
      <li>Nonionic foaming agent</li>
      <li>Drilling Detergent</li>
      <li>Monoethylene Glycol</li>
      <li>Triethylene Glycol</li>
      <li>PAC - Polyanionic Cellulose</li>
      <li>Carboxymethyl Cellulose / CMC</li>
      <li>XC Polymer Xanthan Gum based</li>
      <li>Mono Ethanol Amine</li>
      <li>Sulfonated Asphalt</li>
      <li>Calcium Bromide Liquid 52%</li>
      <li>Primary & Secondary Emulsifier</li>
      <li>Corrosion Inhibitor Imidazoline Based</li>
      <li>Demulsifier Concentrate</li>
      <li>Pour Point Depressant</li>
      <li>Defoamers- Glycol, Silicone and Ethoxylate based</li>
      <li>Organophilic Clay</li>
      <li>N Methyl Aniline</li>
      <li>Methyl Diethylene Glycol</li>
      <li>Mud Thinner</li>
      <li>Mud Wetting Agent</li>
    </ul>
    <p>
      We would be delighted to discuss how our solutions can support your operations. Kindly advise the next steps to explore collaboration.
    </p>
    <p>Looking forward to your response.</p>
    <p style="margin-top:20px;">
      Best Regards,<br><br>
      <strong>Mehul Parmar</strong><br>
      Director – Commercial & Technical<br>
      Cell Phone: <a href="tel:+971554306280" style="color:#0066cc; text-decoration:none;">+971 554306280</a>
    </p>
    <hr style="border:0; border-top:1px solid #ccc; margin:20px 0;">
    <table style="font-size:13px; color:#333; font-family:Arial, sans-serif;">
      <tr>
        <td style="padding-right:10px; vertical-align:top;">
          <img src="https://media.licdn.com/dms/image/v2/D4D0BAQG4B_2SfqHmHQ/company-logo_200_200/company-logo_200_200/0/1706868984894/corofy_llc_logo?e=1759363200&v=beta&t=IRuzQ2YcCU9pPdvTAn2h0L3aXKAFB_ZtJ2EFBMandGU" 
             alt="Corofy Logo" 
             style="height:50px; width:auto;" />
        </td>
        <td style="vertical-align:top;">
          <strong>Corofy LLC</strong><br>
          510 – Goldcrest Executive, Cluster C, JLT – Dubai – United Arab Emirates<br>
          Tel: <a href="tel:+97142715611" style="color:#0066cc; text-decoration:none;">+971 4 271 5611</a> | 
          <a href="http://www.corofychem.com" style="color:#0066cc; text-decoration:none;">www.corofychem.com</a><br>
          Email: <a href="mailto:mehul@corofychem.com" style="color:#0066cc; text-decoration:none;">mehul@corofychem.com</a><br>
          <span style="color:#777;">ISO 9001:2015 Certified from UKAS Management Systems</span>
        </td>
      </tr>
    </table>
  </body>
</html>""",

    "Lubricant": """<!DOCTYPE html>
<html>
  <body style="font-family: Arial, sans-serif; font-size: 14px; color: #333; line-height: 1.6; margin: 0; padding: 0;">
    <p>Hi {{LeadName}},</p>
    <p>Greetings from <b>Corofy</b>!</p>
    <p>
      We are a committed team of professionals supplying Specialty Chemicals for the Lubricants and Grease industry, with ISO 9001:2015 certification from UKAS Management Systems. With warehouses in the UAE and India, and ready stock in both regions, we ensure seamless supply to global clients. Direct shipments from UAE, India, and China are also arranged on request.
    </p>
    <p>Key Lubricant Chemicals we offer include:</p>
    <ul style="margin:0; padding-left:18px;">
      <li>Monoethylene Glycol</li>
      <li>Diethylene Glycol</li>
      <li>Urea Solution / Diesel Exhaust Fluid / AdBlue</li>
      <li>Total Base Number Improver Calcium based</li>
      <li>Zinc Booster</li>
      <li>Dispersant / Polyisobutylene Succinimide / PIBSI</li>
      <li>Additive Packages for Petro and Diesel Engine</li>
      <li>Pour Point Depressant</li>
      <li>Brake Fluid DOT 3 & DOT 4</li>
    </ul>
    <p>
      We would be glad to explore opportunities to work with your esteemed organization. Kindly let us know how we may proceed.
    </p>
    <p>Looking forward to your response.</p>
    <p style="margin-top:20px;">
      Best Regards,<br><br>
      <strong>Mehul Parmar</strong><br>
      Director – Commercial & Technical<br>
      Cell Phone: <a href="tel:+971554306280" style="color:#0066cc; text-decoration:none;">+971 554306280</a>
    </p>
    <hr style="border:0; border-top:1px solid #ccc; margin:20px 0;">
    <table style="font-size:13px; color:#333; font-family:Arial, sans-serif;">
      <tr>
        <td style="padding-right:10px; vertical-align:top;">
          <img src="https://media.licdn.com/dms/image/v2/D4D0BAQG4B_2SfqHmHQ/company-logo_200_200/company-logo_200_200/0/1706868984894/corofy_llc_logo?e=1759363200&v=beta&t=IRuzQ2YcCU9pPdvTAn2h0L3aXKAFB_ZtJ2EFBMandGU" 
             alt="Corofy Logo" 
             style="height:50px; width:auto;" />
        </td>
        <td style="vertical-align:top;">
          <strong>Corofy LLC</strong><br>
          510 – Goldcrest Executive, Cluster C, JLT – Dubai – United Arab Emirates<br>
          Tel: <a href="tel:+97142715611" style="color:#0066cc; text-decoration:none;">+971 4 271 5611</a> | 
          <a href="http://www.corofychem.com" style="color:#0066cc; text-decoration:none;">www.corofychem.com</a><br>
          Email: <a href="mailto:mehul@corofychem.com" style="color:#0066cc; text-decoration:none;">mehul@corofychem.com</a><br>
          <span style="color:#777;">ISO 9001:2015 Certified from UKAS Management Systems</span>
        </td>
      </tr>
    </table>
  </body>
</html>"""
}

DEFAULT_TEMPLATE = """<!DOCTYPE html>
<html>
  <body style="font-family: Arial, sans-serif; font-size: 14px; color: #333; line-height: 1.6; margin: 0; padding: 0;">
    <p>Hi {{LeadName}},</p>
    <p>Greetings from <b>Corofy</b>!</p>
    <p>
      {{BodyContent}}
    </p>
    <p>Looking forward to your response.</p>
    <p style="margin-top:20px;">
      Best Regards,<br><br>
      <strong>Mehul Parmar</strong><br>
      Director – Commercial & Technical<br>
      Cell Phone: <a href="tel:+971554306280" style="color:#0066cc; text-decoration:none;">+971 554306280</a>
    </p>
    <hr style="border:0; border-top:1px solid #ccc; margin:20px 0;">
    <table style="font-size:13px; color:#333; font-family:Arial, sans-serif;">
      <tr>
        <td style="padding-right:10px; vertical-align:top;">
          <img src="https://media.licdn.com/dms/image/v2/D4D0BAQG4B_2SfqHmHQ/company-logo_200_200/company-logo_200_200/0/1706868984894/corofy_llc_logo?e=1759363200&v=beta&t=IRuzQ2YcCU9pPdvTAn2h0L3aXKAFB_ZtJ2EFBMandGU" 
             alt="Corofy Logo" 
             style="height:50px; width:auto;" />
        </td>
        <td style="vertical-align:top;">
          <strong>Corofy LLC</strong><br>
          510 – Goldcrest Executive, Cluster C, JLT – Dubai – United Arab Emirates<br>
          Tel: <a href="tel:+97142715611" style="color:#0066cc; text-decoration:none;">+971 4 271 5611</a> | 
          <a href="http://www.corofychem.com" style="color:#0066cc; text-decoration:none;">www.corofychem.com</a><br>
          Email: <a href="mailto:mehul@corofychem.com" style="color:#0066cc; text-decoration:none;">mehul@corofychem.com</a><br>
          <span style="color:#777;">ISO 9001:2015 Certified from UKAS Management Systems</span>
        </td>
      </tr>
    </table>
  </body>
</html>"""

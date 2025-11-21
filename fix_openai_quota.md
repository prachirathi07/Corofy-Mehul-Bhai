# Fix OpenAI "Insufficient Quota" Error (Even With Balance)

## The Problem
You have balance in your OpenAI account, but all API calls return "429 - insufficient_quota" errors.

## Most Common Cause
**API key was created when account balance was $0**

OpenAI has a known issue where API keys created when the account had zero balance may not work even after you add funds.

## Solution Steps

### Step 1: Verify Your Balance
1. Go to: https://platform.openai.com/account/billing
2. Confirm you have a positive balance (e.g., $5+)
3. Check that your payment method is valid

### Step 2: Create a NEW API Key
**This is the most important step!**

1. Go to: https://platform.openai.com/api-keys
2. **Delete your current API key** (or just create a new one and don't delete the old one yet)
3. Click "Create new secret key"
4. Give it a name (e.g., "New Key - After Adding Balance")
5. Copy the new key immediately (you won't see it again)

### Step 3: Update Your .env File
1. Open your `.env` file
2. Replace the old `OPENAI_API_KEY` value with the new key:
   ```
   OPENAI_API_KEY=sk-proj-...your-new-key-here...
   ```
3. Save the file

### Step 4: Test the New Key
Run the diagnostic script:
```bash
python test_openai_connection.py
```

You should now see ✅ success messages instead of ❌ errors.

## Alternative Solutions (If New Key Doesn't Work)

### Option A: Add More Funds
Sometimes adding a small amount ($5-10) even if you have balance can refresh the account status.

### Option B: Check Usage Limits
1. Go to: https://platform.openai.com/account/limits
2. Check if there are any hard limits set
3. Remove or increase limits if needed

### Option C: Check Billing Method
1. Go to: https://platform.openai.com/account/billing
2. Verify if you're on "Prepaid" or "Postpaid"
3. If on prepaid, ensure you have credits available
4. If on postpaid, ensure payment method is valid

### Option D: Contact OpenAI Support
If none of the above works:
1. Go to: https://help.openai.com/
2. Submit a support ticket explaining:
   - You have balance but getting quota errors
   - You've tried creating a new API key
   - Include your account email

## Quick Test After Fix
Once you update the API key, test it:
```bash
python test_openai_connection.py
```

Then test email personalization:
```bash
python test_personalization.py
```

## Why This Happens
OpenAI's system sometimes "locks" API keys that were created when the account had zero balance, even after funds are added. Creating a new key after adding balance usually resolves this.


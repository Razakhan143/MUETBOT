    
import os
from datetime import datetime
import asyncio
from dotenv import load_dotenv
from app_main.api import retriever_qa
from data import data_processing, news_data_fetcher
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone
load_dotenv()


async def main():
    # detting files
    OUTPUT_FILE = os.path.join("data", "website_documents", "muet_data.txt")
    file_name = os.path.join("data", "website_documents", "muet_circular_data.txt")
    
    # # Data Extraction (Uncomment if you want to re-fetch and process data)

    # 1. Define the Pakistan timezone
    pk_tz = timezone('Asia/Karachi')
    # 2. Initialize scheduler with that timezone
    scheduler = BackgroundScheduler(timezone=pk_tz)
    # 3. Schedule the job (e.g., run at 8:30 AM and 4:30 PM)
    run_time = datetime(2026, 1, 1, 12, 00, 0) # December 25, 2025, at 2:30 PM
    scheduler.add_job(await data_processing.run_data_extraction_whole(OUTPUT_FILE), 'date', run_date=run_time)
    
    scheduler.add_job(await news_data_fetcher.main(file_name), 'cron', hour='12', minute='0')
    # Add the job
    scheduler.start()

    # Initialize Chain
    flag = True
    file_paths = [OUTPUT_FILE, file_name]
    qa_chain = retriever_qa(file_paths, flag)
    
    if qa_chain is None:
        print("Failed to initialize QA Chain. Exiting.")
        return

    print("\n🎓 MUET Chatbot Ready! (Type 'exit' to quit)")
    
    while True:
        query = input('\nUser: ')
        if query.lower() in ['exit', 'bye', 'escape', 'quit']:
            print("Goodbye!")
            break
        
        if not query.strip():
            continue

        try:
            # Most modern chains return a string or a dict with a specific key
            response = qa_chain.invoke(query) # Simplified invoke
            
            # If your chain returns a dict, extract the result
            if isinstance(response, dict):
                answer = response.get("result", response.get("answer", str(response)))
            else:
                answer = response

            print(f"\nAI Response: {answer}")
        except Exception as e:
            print(f"❌ Error during query: {str(e)}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProcess stopped by user.")
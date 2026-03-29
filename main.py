# main.py
import os
from app.core.analyzer import analyze_shelf_image
from app.core.chat import ShelfChatSession
from app.core.rag import save_audit, get_database_stats

IMAGE_PATH = "images/test_shelf.jpg"


def main():
    print("\n" + "="*55)
    print("🏪  SHELFVISION AI — Retail Compliance Chat")
    print("="*55)

    # Ask for store name — this is how RAG tracks history per store
    store_name = input("\n📍 Enter store name (or press Enter for 'Test Store'): ").strip().lower()
    if not store_name:
        store_name = "Test Store"

    # Show database stats before starting
    stats = get_database_stats()
    if stats["total_audits"] > 0:
        print(f"\n📚 Database: {stats['total_audits']} past audits found")
        print(f"   Stores tracked: {', '.join(stats['stores'])}")
        print(f"   Average score: {stats['average_score']}/100")
    else:
        print("\n📚 Database: No past audits yet — this will be the first!")

    # Analyze image
    print(f"\n⏳ Analyzing shelf for {store_name}...")
    analysis = analyze_shelf_image(IMAGE_PATH)
    print(f"✅ Analysis complete! Score: {analysis.compliance_score}/100")

    # Save to ChromaDB automatically
    notes = input("📝 Add audit notes (or press Enter to skip): ").strip()
    record = save_audit(
        analysis=analysis,
        store_name=store_name,
        image_path=IMAGE_PATH,
        notes=notes
    )
    print(f"💾 Audit ID: {record.audit_id}")

    # Start chat session with RAG
    session = ShelfChatSession(analysis=analysis, store_name=store_name)
    print(f"🏷️  Brands: {', '.join(analysis.brands_detected)}")
    print(f"⚠️  Violations: {len(analysis.violations)} found")

    print("\n" + "-"*55)
    print("💬 Chat started! RAG is active — AI knows your history.")
    print("   Type 'history' to see all past audits")
    print("   Type 'stats' to see database statistics")
    print("   Type 'save' to save conversation log")
    print("   Type 'quit' to exit")
    print("-"*55 + "\n")

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue

        if user_input.lower() == "quit":
            session.save_conversation("logs/conversation_log.txt")
            print("👋 Goodbye!")
            break

        elif user_input.lower() == "save":
            session.save_conversation("logs/conversation_log.txt")
            print("💾 Conversation saved!\n")
            continue

        elif user_input.lower() == "stats":
            stats = get_database_stats()
            print(f"\n📊 Database Stats:")
            print(f"   Total audits: {stats['total_audits']}")
            print(f"   Stores: {', '.join(stats['stores'])}")
            print(f"   Average score: {stats.get('average_score', 'N/A')}/100\n")
            continue

        elif user_input.lower() == "history":
            from app.core.rag import get_store_history
            history = get_store_history(store_name)
            if not history:
                print(f"\n📭 No history found for {store_name}\n")
            else:
                print(f"\n📚 Audit History for {store_name}:")
                for audit in history:
                    meta = audit["metadata"]
                    print(f"   [{meta['audit_date']}] "
                          f"Score: {meta['compliance_score']}/100 | "
                          f"Violations: {meta['violations_count']} | "
                          f"ID: {audit['audit_id']}")
                print()
            continue

        response = session.chat(user_input)
        print(f"\n🤖 ShelfVision AI: {response}\n")


if __name__ == "__main__":
    main()
import requests
import json

# Test FPL import functionality
def test_fpl_import():
    base_url = "http://localhost:8081"
    
    # Test with a real FPL entry ID (you can replace this with any valid entry ID)
    entry_id = 123456  # Replace with a real FPL entry ID
    
    print(f"Testing FPL import for entry ID: {entry_id}")
    
    # Test the import endpoint
    import_url = f"{base_url}/api/team/import/fpl-entry?userId=10"
    import_data = {"entryId": entry_id}
    
    try:
        response = requests.post(import_url, json=import_data)
        print(f"Import response status: {response.status_code}")
        print(f"Import response: {response.text}")
        
        if response.status_code == 200:
            # Test getting team players
            players_url = f"{base_url}/api/team/players?userId=10"
            players_response = requests.get(players_url)
            print(f"Players response status: {players_response.status_code}")
            print(f"Players response: {players_response.text}")
        
    except Exception as e:
        print(f"Error testing FPL import: {e}")

if __name__ == "__main__":
    test_fpl_import()

document.addEventListener('DOMContentLoaded', () => {
    //Create a new issue button
    const createIssueButton = document.getElementById('createIssueButton');
    createIssueButton.addEventListener('click', async () => {

        const fullName = document.getElementById('fullName').value;
        const issueTitle = document.getElementById('issueTitle').value;
        const issueDescription = document.getElementById('issueDescription').value;

        if (fullName && issueTitle && issueDescription) {
            try {
                const response = await fetch('/create_jira_issue', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        full_name: fullName,
                        issue_title: issueTitle,
                        issue_description: issueDescription
                    })
                });
                
                //converting json to js object
                const data = await response.json();

                if (response.ok) {
                    alert(`Issue created successfully! Issue ID: ${data.issue_key}`);
                } 
                else {
                    alert(`Failed to create issue: ${data.message}`);
                }
            }
            catch (error) {
                console.error('Error creating issue:', error);
                alert('An error occurred while creating the issue.');
            }s
        }
        else {
            alert('Please fill in all fields.');
        }
    });

    //Get an issue's status
    const issueStatusButton = document.getElementById('issueStatusButton');
    issueStatusButton.addEventListener('click', async () => {

        const issueId = document.getElementById('issueId').value;

        if (issueId) {
            try {
                const body = JSON.stringify({issue_id: issueId})
                const response = await fetch('/get_jira_issue_status', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body
                });
                
                const data = await response.json();
                //console.log('Response data:', data);

                if (response.ok) {
                    alert(`Here is the status: ${data.issue_status}`);
                } 
                else {
                    alert(`Failed to get issue status: ${data.message}`);
                }
            } 
            catch (error) {
                console.error('Error getting issue status:', error);
                alert('An error occurred while getting issue status');
            }
        }
        else {
            alert('Please enter the issue ID in the expected format.');
        }
    });

    //virtual assistant chat box
    const chatBoxButton = document.getElementById('chatBoxButton');
    chatBoxButton.addEventListener('click', async () => {
        chatBoxButton.textContent = 'Processing...';
        const chatBoxPrompt = document.getElementById('chatBox').value;

        if (chatBoxPrompt) {
            try {
                const body = JSON.stringify({chat_box_prompt: chatBoxPrompt})
                const response = await fetch('/virtual_assistant_response', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body
                });
                console.log('here body', body);
                
                const data = await response.json();
                console.log('here2 Response data:', data);

                if (response.ok) {
                    //alert(`Here is the response to your question: ${data.data}`);
                    data.data = data.data.replace(/Step/g, "\nStep");
                    document.getElementById('chatBox').value = data.data;
                    chatBoxButton.textContent = 'Send';                } 
                else {
                    alert(`Failed to get a response to your question: ${data.message}`);
                }
            } 
            catch (error) {
                console.error('Error getting a response to your question:', error);
                alert('An error occurred while getting a response to your question');
            }
        }
        else {
            alert('Please enter your question and click on the Send button');
        }
    });
});

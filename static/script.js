let fetchedData = null;  // Store the fetched data to be used for PDF generation later

async function fetchComments() {
    const query = document.getElementById("query").value;

    if (!query) {
        alert("Please enter a search query.");
        return;
    }

    try {
        // Start measuring time for processing speed
        const startTime = performance.now();
    
        // Fetch comments from the server
        const response = await fetch("http://127.0.0.1:5000/comments", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ query: query })
        });
    
        // Check if response is not okay (non-2xx status)
        if (!response.ok) {
            const errorData = await response.json();
            console.error('Error fetching comments:', errorData);
            alert(errorData.error || "An error occurred while fetching comments.");
            return;
        }
    
        const data = await response.json();
    
        // Clean each comment before further processing
        const cleanedComments = data.sentiments.map((item) => ({
            ...item,
            comment: cleanTextForYouTube(item.comment) // Clean text but keep emojis visible
        }));
    
        // Translate each cleaned comment
        const translatedComments = await translateComments(cleanedComments);
    
        // Calculate processing speed in comments per second
        const endTime = performance.now();
        const processingTime = (endTime - startTime) / 1000; // Time in seconds
        const commentsPerSecond = data.sentiments.length / processingTime;
    
        // Store the fetched data for later use in PDF generation
        fetchedData = {
            translatedComments: translatedComments,
            summary: data.summary,
            chart: data.chart,
            accuracy: data.accuracy,
            commentsPerSecond: commentsPerSecond
        };
    
        // Update UI with translated comments, sentiment data, processing speed, and accuracy
        updateUI(translatedComments, data.summary, data.chart, data.accuracy, commentsPerSecond);
    
    } catch (error) {
        console.error("Error during fetch process:", error);
        alert("Failed to connect to the server. Please check your network or server status.");
    }
}    

// Text cleaning function for YouTube comments (as provided before)
function cleanTextForYouTube(text) {
    text = text.replace(/([\u2764\u1F601-\u1F64F\u1F680-\u1F6FF\u1F30D-\u1F567\u1F970\u1F44D\u1F44E\u1F525\u1F499\u1F4AF\u1F60D\u1F622\u1F62D\u1F648\u1F4A9\u1F92A\u1F389\u1F600])/g, match => {
        const emojiDictionary = {
            "❤️": "love",
            "😁": "happy",
            "💥": "explosion",
            "🌍": "earth",
            "💖": "love",
            "👍": "like",
            "👎": "dislike",
            "🔥": "fire",
            "💙": "blue heart",
            "💯": "hundred",
            "😍": "in love",
            "😢": "crying",
            "😌": "content",
            "🐍": "snake",
            "👀": "eyes",
            "🎉": "celebration",
        };

        return emojiDictionary[match] || match;
    });

    text = text.replace(/#\w+/g, "");
    text = text.replace(/@\w+/g, "");
    text = text.replace(/([!?])\1+/g, "$1");
    text = text.replace(/\.{2,}/g, ".");
    text = text.replace(/subscribe\s+to\s+my\s+channel|check\s+my\s+profile/gi, "");
    text = text.replace(/\s+/g, " ").trim();

    return text;
}

// Translate all comments using LibreTranslate API
async function translateComments(sentiments) {
    const translatedComments = await Promise.all(sentiments.map(async (sentiment) => {
        const translatedText = await translateText(sentiment.comment);
        return {
            ...sentiment,
            comment: translatedText
        };
    }));

    return translatedComments;
}

// Translate a single comment using LibreTranslate API
async function translateText(comment) {
    try {
        const res = await fetch("https://libretranslate.com/translate", {
            method: "POST",
            body: JSON.stringify({
                q: comment,
                source: "auto",
                target: "en",
                format: "text",
                alternatives: 3,
                api_key: "" // Optionally, add your API key here if required
            }),
            headers: { "Content-Type": "application/json" }
        });

        const result = await res.json();
        return result.translatedText || comment;
    } catch (error) {
        console.error("Translation error:", error);
        return comment;
    }
}

function updateUI(sentiments, summary, chart, accuracy, commentsPerSecond) {
    const resultsDiv = document.getElementById("results");
    const summaryDiv = document.getElementById("summary");
    const chartContainer = document.getElementById("chart-container");
    const accuracyDiv = document.getElementById("accuracy");
    const speedDiv = document.getElementById("speed");

    resultsDiv.innerHTML = sentiments.length
        ? sentiments.map(item => `
            <div class="comment">
                <p>${item.comment}</p>
                <p class="sentiment-label ${getSentimentClass(item.sentiment)}">${item.sentiment}</p>
            </div>
        `).join("")
        : "<p>No comments found.</p>";

    summaryDiv.innerHTML = `
        <p>Total Positive: ${summary.Positive}</p>
        <p>Total Negative: ${summary.Negative}</p>
        <p>Total Neutral: ${summary.Neutral}</p>
    `;

    if (chart) {
        chartContainer.innerHTML = `<img src="data:image/png;base64,${chart}" alt="Sentiment Chart">`;
    } else {
        chartContainer.innerHTML = "<p>No chart available.</p>";
    }

    accuracyDiv.innerText = accuracy || "Accuracy data not available.";
    speedDiv.innerHTML = `Processing Speed: ${commentsPerSecond.toFixed(2)} comments per second`;
}

// Function to return the appropriate sentiment class
function getSentimentClass(sentiment) {
    if (sentiment === "Positive") {
        return "sentiment-positive";
    } else if (sentiment === "Negative") {
        return "sentiment-negative";
    } else {
        return "sentiment-neutral";
    }
}

// Function to generate the PDF report and trigger the download when the button is clicked
document.getElementById("download-report").addEventListener("click", () => {
    if (fetchedData) {
        const { translatedComments, summary, chart, accuracy, commentsPerSecond } = fetchedData;
        generatePDFReport(translatedComments, summary, chart, accuracy, commentsPerSecond);
    } else {
        alert("No data available. Please fetch comments first.");
    }
});

// Function to generate the PDF report and trigger the download
function generatePDFReport(translatedComments, summary, chart, accuracy, commentsPerSecond) {
    const { jsPDF } = window.jspdf; // Import jsPDF from window object
    const doc = new jsPDF();

    let currentY = 20; // Start Y position for the first page

    // Add title
    doc.setFontSize(18);
    doc.text("Sentiment Analysis Report", 14, currentY);
    currentY += 10; // Move down after the title

    // Add Sentiments Section
    doc.setFontSize(12);
    doc.text("Sentiments:", 14, currentY);
    currentY += 10; // Move down for Sentiments section

    translatedComments.forEach((item, index) => {
        doc.text(`${index + 1}. ${item.comment} (${item.sentiment})`, 14, currentY);
        currentY += 10; // Move down after each comment

        // Check if the content has reached the bottom of the page
        if (currentY > 270) { // 270 is roughly the bottom of the page
            doc.addPage(); // Add a new page
            currentY = 20; // Reset Y position for new page
            doc.setFontSize(12); // Reset font size for the new page
            currentY += 10; // Move down for the next content
        }
    });

    doc.addPage(); // Add a new page
    currentY = 20; // Reset Y position for new page
    doc.setFontSize(12); // Reset font size for the new page
    currentY += 10; // Move down for the next content

    // Add Summary Section
    doc.text("Summary:", 14, currentY);
    currentY += 10; // Move down after "Summary" title
    doc.text(`Total Positive: ${summary.Positive}`, 14, currentY);
    currentY += 5;
    doc.text(`Total Negative: ${summary.Negative}`, 14, currentY);
    currentY += 5;
    doc.text(`Total Neutral: ${summary.Neutral}`, 14, currentY);
    currentY += 10;

    // Add Processing Speed
    doc.text(`Processing Speed: ${commentsPerSecond.toFixed(2)} comments per second`, 14, currentY);
    currentY += 10;

    // Add Accuracy
    doc.text(`Accuracy: ${accuracy || "Not available"}`, 14, currentY);
    currentY += 10;

    // Add Chart (if available)
    if (chart) {
        // Ensure the chart is a valid base64 string
            doc.addImage(`data:image/png;base64,${chart}`, 'PNG', 30, currentY, 100, 100);
            currentY += 100; // Adjust position after adding the chart
    } else {
        console.error("Invalid chart data.");
    }


    // Save the PDF with a filename
    doc.save("sentiment_analysis_report.pdf");
}

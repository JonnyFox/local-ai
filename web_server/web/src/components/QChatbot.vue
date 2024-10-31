<script setup>
import { nextTick, ref } from 'vue'
import { QSpinnerDots } from 'quasar'

const query = ref('')
const results = ref([])
const thinking = ref(false)
const resultsContainer = ref(null)
const chatUUID = ref(1)

const search = async () => {
  try {
    const question = query.value
    query.value = ''
    thinking.value = true

    // Add the new query to results
    results.value.push({ text: question, role: 'human' })
    results.value.push({ text: '', role: 'AI' })
    nextTick(scrollToBottom)

    // Initiate a POST request with streaming response using fetch
    const response = await fetch('http://localhost:8000/api/search/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        query: question,
        chat_uuid: chatUUID.value
      })
    })
    if (!response.ok) {
      throw new Error('Network response was not ok')
    }

    // Process the response as a readable stream
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let accumulatedText = ''

    while (true) {
      const { done, value } = await reader.read()

      if (thinking.value) {
        thinking.value = false
      }

      if (done) break
      const currentText = decoder.decode(value, { stream: true })
      console.log('Streaming data:', currentText)
      accumulatedText += currentText

      // Update the last AI item in results with the streamed data
      const lastAIMessage = results.value.slice().reverse().find((item) => item.role === 'AI')
      if (lastAIMessage) {
        lastAIMessage.text = accumulatedText
        nextTick(scrollToBottom)
      }
    }

    // Finish processing
    nextTick(scrollToBottom)
  } catch (error) {
    results.value.push({ text: 'Error talking to the model... Maybe try again?', role: 'AI', type: 'error' })
    console.error('Error fetching streaming data:', error)
  } finally {
    thinking.value = false
  }
}

const scrollToBottom = () => {
  if (resultsContainer.value) {
    resultsContainer.value.scrollTop = resultsContainer.value.scrollHeight
  }
}
</script>

<template>
  <div>
    <div class="chat-container">
      <div v-if="results.length" class="results" ref="resultsContainer">
        <div v-for="(result, index) in results" :key="index" :class="{ 'result-item': true, 'AI': result.role === 'AI', 'error': result.type === 'error' }">
          <div v-html="result.text" />
          <q-spinner-dots color="grey" size="1em" class="q-ml-1" v-if="thinking && index === results.length - 1"/>
        </div>
      </div>
      <div class="chat-box">
        <input v-model="chatUUID" placeholder="Chat UUID" class="chat-uuid" :disabled="thinking"/>
        <q-input dense borderless v-model="query" class="chat-input" placeholder="Ask a question" @keyup.enter="search" :readonly="thinking">
          <template v-slot:after>
            <q-btn round dense flat icon="send" @click="search" :loading="thinking"/>
          </template>
        </q-input>
      </div>
    </div>
  </div>
</template>

<style scoped>
body {
  margin: 0;
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

.chat-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
  height: 100vh;
  background-color: #f7f7f8;
}

.chat-uuid {
  width: 3rem;
  border: none;
  outline: none;
  border-right: 1px solid #e0e0e0;
  text-align: center;
}

.chat-box {
  display: flex;
  width: 100%;
  max-width: 800px;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 0.5rem;
  margin-bottom: 1rem;
}

.chat-input {
  flex: 1;
  padding: 0.5rem;
  font-size: 1rem;
  border: none;
  outline: none;
}

.chat-button {
  padding: 0 1rem;
  font-size: 1rem;
  border: none;
  background-color: #007bff;
  color: white;
  border-radius: 5px;
  cursor: pointer;
}

.chat-button:hover {
  background-color: #0056b3;
}

.results {
  width: 100%;
  max-width: 800px;
  margin-top: 1rem;
  overflow-y: scroll;
  scrollbar-width: thin;
  scrollbar-color: #f7f7f8 #f7f7f8;
}

.results:hover {
  scrollbar-color: #e0e0e0 #f7f7f8;
}

.result-item {
  background: white;
  border: 1px solid #e0e0e0;
  padding: 1rem;
  margin-bottom: 0.5rem;
  text-align: right;
  margin-left: 5rem;
  border-radius: 1rem 1rem 0 1rem;
  width: fit-content;
  margin-right: 0;
  margin-left: auto;
}

.AI {
  background-color: #eeeefc;
  text-align: left;
  margin-left: 0;
  margin-right: 5rem;
  border-radius: 1rem 1rem 1rem 0;
  width: fit-content;
}

.error {
  color: red;
}
</style>

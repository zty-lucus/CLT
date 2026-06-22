<template>
  <div class="file-upload">
    <!-- 文件选择区域 -->
    <div
      class="upload-drop-zone"
      :class="{ 'is-dragover': isDragover, 'is-uploading': uploading }"
      @dragover.prevent="isDragover = true"
      @dragleave.prevent="isDragover = false"
      @drop.prevent="handleDrop"
      @click="triggerFileInput"
    >
      <input
        ref="fileInputRef"
        type="file"
        :multiple="multiple"
        :accept="acceptString"
        style="display: none"
        @change="handleFileSelect"
      />

      <div v-if="!uploading" class="drop-content">
        <el-icon :size="48" color="#c0c4cc"><UploadFilled /></el-icon>
        <p class="drop-text">点击选择文件或拖拽文件到此处</p>
        <p class="drop-hint">
          支持 {{ acceptHint }}，单个文件最大 {{ maxSizeText }}
        </p>
        <p v-if="multiple" class="drop-hint">支持同时选择多个文件（最多10个）</p>
      </div>
      <div v-else class="drop-content">
        <el-icon :size="48" color="#409eff" class="is-loading"><UploadFilled /></el-icon>
        <p class="drop-text">正在上传...</p>
      </div>
    </div>

    <!-- 已选文件列表 -->
    <div v-if="selectedFiles.length > 0 && !uploading" class="file-list">
      <div v-for="(file, index) in selectedFiles" :key="index" class="file-item">
        <div class="file-info">
          <el-icon :size="24" color="#409eff">
            <Document />
          </el-icon>
          <div class="file-detail">
            <span class="file-name" :title="file.name">{{ file.name }}</span>
            <span class="file-size">{{ formatSize(file.size) }}</span>
          </div>
        </div>
        <el-button
          link
          type="danger"
          size="small"
          @click.stop="removeFile(index)"
        >
          <el-icon><Close /></el-icon>
        </el-button>
      </div>
    </div>

    <!-- 上传进度 -->
    <div v-if="uploading" class="upload-progress">
      <div class="progress-info">
        <span>上传进度</span>
        <span>{{ progress }}%</span>
      </div>
      <el-progress :percentage="progress" :stroke-width="12" :show-text="false" />
      <p class="progress-file">{{ uploadingFileName }}</p>
    </div>

    <!-- 已上传文件列表（展示已上传成功的文件） -->
    <div v-if="uploadedFiles.length > 0" class="uploaded-files">
      <div class="uploaded-header">
        <span>已上传的文件 ({{ uploadedFiles.length }})</span>
      </div>
      <div v-for="file in uploadedFiles" :key="file.id" class="uploaded-item">
        <div class="file-info">
          <el-icon :size="24" :color="getFileIconColor(file.file_type)">
            <component :is="getFileIcon(file.file_type)" />
          </el-icon>
          <div class="file-detail">
            <span class="file-name" :title="file.original_name">{{ file.original_name }}</span>
            <span class="file-size">{{ formatSize(file.file_size) }}</span>
          </div>
        </div>
        <div class="file-actions">
          <el-button link type="primary" size="small" @click="handleDownload(file)">
            下载
          </el-button>
          <el-button link type="danger" size="small" @click="handleDelete(file)">
            删除
          </el-button>
        </div>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div v-if="selectedFiles.length > 0 && !uploading" class="upload-actions">
      <el-button @click="clearFiles">取消</el-button>
      <el-button type="primary" @click="startUpload">
        <el-icon><Upload /></el-icon>
        上传 ({{ selectedFiles.length }}个文件)
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { fileApi } from '@/api/file'

const props = defineProps({
  /** 是否支持多文件选择 */
  multiple: {
    type: Boolean,
    default: false,
  },
  /** 允许的文件类型（MIME类型，逗号分隔） */
  accept: {
    type: String,
    default: '',
  },
  /** 最大文件大小（MB），默认50MB */
  maxSize: {
    type: Number,
    default: 50,
  },
  /** 是否显示已上传的文件列表 */
  showUploaded: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['upload-success', 'upload-error', 'file-delete'])

// 文件输入
const fileInputRef = ref(null)

// 拖拽状态
const isDragover = ref(false)

// 上传状态
const uploading = ref(false)
const progress = ref(0)
const uploadingFileName = ref('')

// 文件列表
const selectedFiles = ref([])
const uploadedFiles = ref([])

// 计算属性
const maxSizeText = computed(() => {
  return props.maxSize >= 1024
    ? `${(props.maxSize / 1024).toFixed(1)}GB`
    : `${props.maxSize}MB`
})

const acceptHint = computed(() => {
  if (props.accept) return props.accept
  return '文档、图片、压缩包、音视频等常见格式'
})

const acceptString = computed(() => {
  if (props.accept) return props.accept
  return '.doc,.docx,.pdf,.txt,.xls,.xlsx,.ppt,.pptx,.jpg,.jpeg,.png,.gif,.bmp,.svg,.webp,.zip,.rar,.7z,.tar,.gz,.mp3,.mp4,.avi,.mov,.wav,.flac'
})

// ============ 文件选择 ============

function triggerFileInput() {
  if (uploading.value) return
  fileInputRef.value?.click()
}

function handleFileSelect(event) {
  const files = Array.from(event.target.files || [])
  addFiles(files)
  // 重置 input，以便可以重复选择同一文件
  event.target.value = ''
}

function handleDrop(event) {
  isDragover.value = false
  const files = Array.from(event.dataTransfer.files || [])
  if (!props.multiple && files.length > 0) {
    addFiles([files[0]])
  } else {
    addFiles(files)
  }
}

function addFiles(files) {
  if (files.length === 0) return

  // 检查数量限制
  if (!props.multiple && files.length > 1) {
    ElMessage.warning('不支持多文件选择，仅选择第一个文件')
    files = [files[0]]
  }

  if (props.multiple && selectedFiles.value.length + files.length > 10) {
    ElMessage.warning('单次最多选择10个文件')
    return
  }

  // 校验文件大小
  const maxBytes = props.maxSize * 1024 * 1024
  for (const file of files) {
    if (file.size > maxBytes) {
      ElMessage.error(`文件「${file.name}」大小超过限制（最大${maxSizeText.value}）`)
      return
    }
    if (file.size === 0) {
      ElMessage.error(`文件「${file.name}」为空，无法上传`)
      return
    }
  }

  selectedFiles.value = [...selectedFiles.value, ...files]
}

function removeFile(index) {
  selectedFiles.value.splice(index, 1)
}

function clearFiles() {
  selectedFiles.value = []
}

// ============ 文件上传 ============

async function startUpload() {
  if (selectedFiles.value.length === 0) return

  uploading.value = true
  progress.value = 0

  try {
    if (selectedFiles.value.length === 1 && !props.multiple) {
      // 单文件上传
      const file = selectedFiles.value[0]
      uploadingFileName.value = file.name
      const res = await fileApi.upload(file, (event) => {
        if (event.total) {
          progress.value = Math.round((event.loaded / event.total) * 100)
        }
      })
      uploadedFiles.value.unshift(res.data)
      ElMessage.success(`文件「${file.name}」上传成功`)
      emit('upload-success', res.data)
    } else {
      // 批量上传
      uploadingFileName.value = `正在上传 ${selectedFiles.value.length} 个文件...`
      const res = await fileApi.uploadMultiple(selectedFiles.value, (event) => {
        if (event.total) {
          progress.value = Math.round((event.loaded / event.total) * 100)
        }
      })
      if (res.data.uploaded) {
        uploadedFiles.value = [...res.data.uploaded, ...uploadedFiles.value]
        ElMessage.success(`成功上传 ${res.data.success_count} 个文件`)
        res.data.uploaded.forEach((f) => emit('upload-success', f))
      }
      if (res.data.failed && res.data.failed.length > 0) {
        res.data.failed.forEach((f) => {
          ElMessage.error(`「${f.filename}」上传失败: ${f.error}`)
          emit('upload-error', f)
        })
      }
    }
    // 清已选文件列表
    clearFiles()
  } catch {
    // 错误已在拦截器中处理
  } finally {
    uploading.value = false
    progress.value = 0
    uploadingFileName.value = ''
  }
}

// ============ 已上传文件操作 ============

async function handleDownload(file) {
  try {
    const res = await fileApi.downloadFile(file.id)
    // 创建 Blob 并触发下载
    const blob = res.data || res
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = file.original_name
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    ElMessage.success('开始下载')
  } catch {
    // 尝试直接打开下载链接
    const downloadUrl = fileApi.getDownloadUrl(file.id)
    window.open(downloadUrl, '_blank')
  }
}

async function handleDelete(file) {
  try {
    await fileApi.deleteFile(file.id)
    uploadedFiles.value = uploadedFiles.value.filter((f) => f.id !== file.id)
    ElMessage.success('文件已删除')
    emit('file-delete', file.id)
  } catch {
    // 错误已在拦截器中处理
  }
}

// ============ 加载已上传文件 ============

async function loadUploadedFiles() {
  if (!props.showUploaded) return
  try {
    const res = await fileApi.getMyFiles(1, 20)
    uploadedFiles.value = res.data.files || []
  } catch {
    uploadedFiles.value = []
  }
}

onMounted(() => {
  loadUploadedFiles()
})

// ============ 工具函数 ============

function formatSize(bytes) {
  if (bytes < 1024) return `${bytes}B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)}MB`
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)}GB`
}

function getFileIcon(ext) {
  const imageTypes = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp']
  const archiveTypes = ['zip', 'rar', '7z', 'tar', 'gz']
  const docTypes = ['doc', 'docx', 'pdf', 'txt', 'xls', 'xlsx', 'ppt', 'pptx']
  if (imageTypes.includes(ext)) return 'PictureFilled'
  if (archiveTypes.includes(ext)) return 'FolderOpened'
  if (docTypes.includes(ext)) return 'Document'
  return 'Document'
}

function getFileIconColor(ext) {
  const imageTypes = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp']
  const archiveTypes = ['zip', 'rar', '7z', 'tar', 'gz']
  if (imageTypes.includes(ext)) return '#67c23a'
  if (archiveTypes.includes(ext)) return '#e6a23c'
  return '#409eff'
}
</script>

<style scoped>
.file-upload {
  width: 100%;
}

/* 拖拽区域 */
.upload-drop-zone {
  border: 2px dashed #dcdfe6;
  border-radius: 8px;
  padding: 32px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  background: #fafafa;
}
.upload-drop-zone:hover {
  border-color: #409eff;
  background: #f0f5ff;
}
.upload-drop-zone.is-dragover {
  border-color: #409eff;
  background: #e6f0ff;
}
.upload-drop-zone.is-uploading {
  cursor: not-allowed;
  border-color: #409eff;
  background: #f0f5ff;
}
.drop-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}
.drop-text {
  font-size: 14px;
  color: #606266;
  margin: 0;
}
.drop-hint {
  font-size: 12px;
  color: #c0c4cc;
  margin: 0;
}

/* 已选文件列表 */
.file-list {
  margin-top: 12px;
  max-height: 200px;
  overflow-y: auto;
}
.file-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  margin-bottom: 6px;
  transition: background 0.2s;
}
.file-item:hover {
  background: #f5f7fa;
}
.file-info {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  min-width: 0;
}
.file-detail {
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.file-name {
  font-size: 13px;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.file-size {
  font-size: 11px;
  color: #909399;
  margin-top: 2px;
}

/* 上传进度 */
.upload-progress {
  margin-top: 16px;
}
.progress-info {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: #606266;
  margin-bottom: 6px;
}
.progress-file {
  font-size: 12px;
  color: #909399;
  margin-top: 6px;
  text-align: center;
}

/* 已上传文件 */
.uploaded-files {
  margin-top: 16px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  overflow: hidden;
}
.uploaded-header {
  padding: 10px 16px;
  background: #f5f7fa;
  font-size: 13px;
  color: #606266;
  border-bottom: 1px solid #ebeef5;
}
.uploaded-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  border-bottom: 1px solid #f5f5f5;
  transition: background 0.2s;
}
.uploaded-item:last-child {
  border-bottom: none;
}
.uploaded-item:hover {
  background: #fafafa;
}
.file-actions {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}

/* 操作按钮 */
.upload-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 16px;
}
</style>
